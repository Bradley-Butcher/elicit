"""Script to extract answers from a document using a Q&A Transformer model."""
from transformers import Pipeline, RobertaTokenizerFast
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import itertools
import warnings

from transformers import Pipeline, RobertaForQuestionAnswering, RobertaTokenizer, get_linear_schedule_with_warmup
from transformers.modeling_outputs import QuestionAnsweringModelOutput
from transformers.pipelines.question_answering import MODEL_FOR_QUESTION_ANSWERING_MAPPING
import torch
from torch.nn import CrossEntropyLoss
from torch.optim import AdamW
from tqdm.auto import tqdm

from elicit.interface import Extraction
from elicit.utils.loading import load_schema
from elicit.utils.dl_utils import QADataset

warnings.filterwarnings("ignore")

model_path = Path(__file__).parent.parent.parent / "models"


def _flatten_answers(answers: Union[List[Dict], List[List[Dict]]]) -> List[Dict]:
    """
    Flatten a list of answers.

    :param answers: List of lists of answers.

    :return: Flattened list of answers.
    """
    if isinstance(answers[0], dict):
        return answers
    else:
        return list(itertools.chain.from_iterable(answers))


def _filter_candidates(answers: List[dict], threshold: float = 0.5) -> str:
    """
    Filter candidates based on their score.

    :param answers: List of candidates.
    :param threshold: Threshold for filtering.

    :return: Filtered list of candidates.
    """
    answers = _flatten_answers(answers=answers)
    return [(a["answer"], a["score"], a["start"], a["end"]) for a in answers if a["score"] > threshold]


def split_question(question: str, context: str, max_length: int = 512) -> Tuple[List[dict[str, str]], int]:
    if len(context) < max_length:
        return [{"question": question, "context": context}]
    else:
        contexts = []
        while len(context) > max_length:
            idx = max(context[:max_length].rfind(i) for i in [".", "\n"])
            if idx == -1:
                idx = max_length
            contexts.append(context[:idx])
            context = context[idx:]
        contexts.append(context)
        return [{"question": question, "context": c} for c in contexts]


def extract_answers(document_text: str, questions: List[str], qna_model: Pipeline, topk: int = 5, threshold: float = 0.3) -> Dict[str, Tuple[str, float, int, int]]:
    """
    Extract answers from a document using a Q&A Transformer model.

    :param document_text: Text Document to extract answers from.
    :param questions: List of questions to extract answers for.
    :param topk: Number of answers to return.
    :param threshold: Threshold for filtering.

    :return: Dictionary of answers.
    """
    question_input = []
    for q in questions:
        qs = split_question(question=q, context=document_text)
        question_input.extend(qs)
    res = qna_model(question_input, top_k=topk)
    return _filter_candidates(res, threshold=threshold)


class RobertaForQuestionAnsweringWithNegatives(RobertaForQuestionAnswering):
    """
    RobertaForQuestionAnswering with a negative class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        token_type_ids: Optional[torch.LongTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        start_positions: Optional[torch.LongTensor] = None,
        end_positions: Optional[torch.LongTensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.roberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0]

        logits = self.qa_outputs(sequence_output)
        start_logits, end_logits = logits.split(1, dim=-1)
        start_logits = start_logits.squeeze(-1).contiguous()
        end_logits = end_logits.squeeze(-1).contiguous()

        total_loss = None
        if start_positions is not None and end_positions is not None:
            # If we are on multi-GPU, split add a dimension
            if len(start_positions.size()) > 1:
                start_positions = start_positions.squeeze(-1)
            if len(end_positions.size()) > 1:
                end_positions = end_positions.squeeze(-1)
            # sometimes the start/end positions are outside our model inputs, we ignore these terms
            ignored_index = start_logits.size(1)
            start_positions = start_positions.clamp(0, ignored_index)
            end_positions = end_positions.clamp(0, ignored_index)

            loss_fct = CrossEntropyLoss(ignore_index=ignored_index)
            start_loss = loss_fct(start_logits, start_positions)
            end_loss = loss_fct(end_logits, end_positions)
            total_loss = (start_loss + end_loss) / 2

        if not return_dict:
            output = (start_logits, end_logits) + outputs[2:]
            return ((total_loss,) + output) if total_loss is not None else output

        return QuestionAnsweringModelOutput(
            loss=total_loss,
            start_logits=start_logits,
            end_logits=end_logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )


def train_qa(dataset: QADataset, qna_model: RobertaForQuestionAnsweringWithNegatives, device: str):
    N = len(dataset)
    train_set, val_set = torch.utils.data.random_split(
        dataset, [N - (N // 10), N // 10])
    train_loader = torch.utils.data.DataLoader(
        train_set, batch_size=8, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_set, batch_size=8)
    optimizer = AdamW(qna_model.parameters(), lr=3e-5)
    num_epochs = 10
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=0, num_training_steps=num_epochs * len(train_loader))
    qna_model.to(device)
    progress_bar = tqdm(
        range(num_epochs * len(train_loader)))

    qna_model.train()
    for epoch in progress_bar:
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = qna_model(**batch)
            loss = outputs[0]
            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            progress_bar.set_postfix(loss=loss.item())
            progress_bar.update(1)
    return qna_model


def load_qa_model(model_directory: str) -> tuple[RobertaForQuestionAnsweringWithNegatives, RobertaTokenizerFast]:
    if (model_directory / "qna_model").exists():
        print("Fine tuned Q&A model found, loading...")
        MODEL_FOR_QUESTION_ANSWERING_MAPPING["neg_roberta"] = "RobertaForQuestionAnsweringWithNegatives"
        qna_tokenizer = RobertaTokenizerFast.from_pretrained(
            "deepset/roberta-base-squad2")
        qna_model = RobertaForQuestionAnsweringWithNegatives.from_pretrained(
            model_directory / "qna_model")
    else:
        print("No fine tuned Q&A model found, loading generic model...")
        MODEL_FOR_QUESTION_ANSWERING_MAPPING["neg_roberta"] = "RobertaForQuestionAnsweringWithNegatives"
        qna_tokenizer = RobertaTokenizerFast.from_pretrained(
            "deepset/roberta-base-squad2")
        qna_model = RobertaForQuestionAnsweringWithNegatives.from_pretrained(
            "deepset/roberta-base-squad2")
    return qna_model, qna_tokenizer
