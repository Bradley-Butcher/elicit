"""Script which uses a Natural Language Inference transfomer model assign extracted Q&A pairs to provided categories."""
from datasets import load_metric
import torch
from torch.optim import AdamW
from torch.nn import CrossEntropyLoss
from transformers import MODEL_FOR_QUESTION_ANSWERING_MAPPING, Pipeline, RobertaForQuestionAnswering, RobertaTokenizer, RobertaTokenizerFast, get_linear_schedule_with_warmup, pipeline
from transformers.modeling_outputs import QuestionAnsweringModelOutput

from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple, Union
import warnings
from elicit.interface import CategoricalLabellingFunction, Extraction
from elicit.generic_labelling_functions.qa_transformer import extract_answers
from elicit.utils.utils import QADataset

from tqdm.auto import tqdm

warnings.filterwarnings("ignore")


def compress(candidates: List[Tuple[str, float, int, int]]) -> Dict[str, float]:
    """
    Compress the list of candidate answers, summing the probabilities where the answer is the same.
    Context returned is the max of the same answer.

    :param candidates: List of candidate answers. Form is [(answer, score, start, end)]. Multiple answers can be the same, but coming from different parts of the document. These are summed together.

    :return: Dictionary of answers and their probabilities.
    """
    prob_dict = DefaultDict(float)
    prob_sum = 0.0
    max_context = {}
    max_candidate = DefaultDict(float)
    for candidate, prob, start, end in candidates:
        if prob > max_candidate[candidate]:
            max_candidate[candidate] = prob
            max_context[candidate] = {"start": start, "end": end}
    for ci in candidates:
        prob_dict[ci[0]] += ci[1]
        prob_sum += ci[1]
    return {k: v / prob_sum for k, v in prob_dict.items()}, max_context


def match_classify(answers: List[Tuple[str, float]], document_text: str, levels: List[str], classification_model: Pipeline, filter_threshold: float, threshold: float) -> Tuple[str, float]:
    """
    Match answers from the Q&A Transformer to the levels of the variable.

    :param answers: List of answers from Q&A Transformer.
    :param doc: Document string.
    :param levels: List of levels for the variable.
    :param threshold: Threshold for the Q&A Transformer. Only answers above this threshold are considered.

    :return: Tuple of the matched level and the confidence of the match.
    """
    candidates = []
    for answer, score, start, end in answers:
        if answer in levels:
            candidates.append((answer, score, start, end))
        else:
            output = classification_model(
                answer,
                [*levels, ""],
                multi_label=True
            )
            candidates += [(output["labels"][i], output["scores"][i] * score, start, end)
                           for i in range(len(output["labels"])) if output["scores"][i] > filter_threshold]
    if not candidates:
        return [Extraction.abstain()]
    compressed_candidates, context = compress(candidates)
    candidates = [(o, s)
                  for o, s in compressed_candidates.items() if s > threshold]

    # create a list of Extraction for each candidate
    extractions = []
    for candidate, score in candidates:
        if candidate == "":
            continue
        extractions.append(Extraction.from_character_startend(
            document_text,
            candidate,
            score,
            context[candidate]["start"],
            context[candidate]["end"]
        ))

    if len(extractions) == 0:
        return [Extraction.abstain()]
    else:
        return extractions


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


class NLILabellingFunction(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)
        self.match_threshold = 0.5
        self.qna_threshold = 0.3

    def load(self, model_directory: Path, device: Union[int, str]) -> None:
        self.device = device
        self.model_directory = model_directory
        self.classifier = pipeline("zero-shot-classification",
                                   model="facebook/bart-large-mnli", device=self.device)
        if (model_directory / "qna_model").exists():
            print("Fine tuned Q&A model found, loading...")
            MODEL_FOR_QUESTION_ANSWERING_MAPPING["neg_roberta"] = "RobertaForQuestionAnsweringWithNegatives"
            self.qna_tokenizer = RobertaTokenizerFast.from_pretrained(
                "deepset/roberta-base-squad2")
            self.qna_model = RobertaForQuestionAnsweringWithNegatives.from_pretrained(
                model_directory / "qna_model")
        else:
            print("No fine tuned Q&A model found, loading generic model...")
            MODEL_FOR_QUESTION_ANSWERING_MAPPING["neg_roberta"] = "RobertaForQuestionAnsweringWithNegatives"
            self.qna_tokenizer = RobertaTokenizerFast.from_pretrained(
                "deepset/roberta-base-squad2")
            self.qna_model = RobertaForQuestionAnsweringWithNegatives.from_pretrained(
                "deepset/roberta-base-squad2")
        self.qna_pipeline = pipeline(
            task='question-answering',
            model=self.qna_model,
            tokenizer=self.qna_tokenizer,
            device=device
        )
        self.loaded = True

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        questions = self.get_schema("questions", variable_name)
        categories = self.get_schema("categories", variable_name)
        final_threshold = 1 / (len(categories) + 1)
        answers = extract_answers(
            document_text,
            questions=questions,
            qna_model=self.qna_pipeline,
            threshold=self.qna_threshold
        )
        extractions = match_classify(
            answers=answers,
            document_text=document_text,
            levels=categories,
            classification_model=self.classifier,
            filter_threshold=self.match_threshold,
            threshold=final_threshold)
        self.push_many(document_name, variable_name, extractions)

    def train(self, data: dict[str, List["Extraction"]]):
        dataset = QADataset(data, self.get_schema(
            "questions"), self.qna_tokenizer)
        N = len(dataset)
        train_set, val_set = torch.utils.data.random_split(
            dataset, [N - (N // 10), N // 10])
        train_loader = torch.utils.data.DataLoader(
            train_set, batch_size=8, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_set, batch_size=8)
        optimizer = AdamW(self.qna_model.parameters(), lr=3e-5)
        num_epochs = 10
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=num_epochs * len(train_loader))
        self.qna_model.to(self.device)
        progress_bar = tqdm(
            range(num_epochs * len(train_loader)))

        self.qna_model.train()
        for epoch in progress_bar:
            for batch in train_loader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                outputs = self.qna_model(**batch)
                loss = outputs[0]
                loss.backward()
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                progress_bar.set_postfix(loss=loss.item())
                progress_bar.update(1)

        self.qna_model.eval()
        print(f"Saving Trained Model to {self.model_directory / 'qna_model'}")
        self.qna_model.save_pretrained(self.model_directory / "qna_model")

    @property
    def labelling_method(self) -> str:
        return "Q&A → NLI Transformer"
