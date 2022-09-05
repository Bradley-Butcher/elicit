"""Script which uses a Natural Language Inference transfomer model assign extracted Q&A pairs to provided categories."""
import torch
from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss, MSELoss

from transformers import AutoTokenizer, pipeline
from transformers import BartForSequenceClassification, BartTokenizerFast

from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple, Union
import warnings

from elicit.interface import CategoricalLabellingFunction, Extraction


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
    candidates = [(cat, sc, st, end)
                  for cat, sc, st, end in candidates if sc > threshold]

    # create a list of Extraction for each candidate
    extractions = []
    for cat, sc, st, end in candidates:
        if cat == "":
            continue
        extractions.append(Extraction.from_character_startend(
            document_text,
            cat,
            sc,
            st,
            end
        ))

    if len(extractions) == 0:
        return [Extraction.abstain()]
    else:
        return extractions


class BartForSequenceClassificationWithNegatives(BartForSequenceClassification):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        decoder_input_ids: Optional[torch.LongTensor] = None,
        decoder_attention_mask: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        decoder_head_mask: Optional[torch.Tensor] = None,
        cross_attn_head_mask: Optional[torch.Tensor] = None,
        encoder_outputs: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        decoder_inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, Seq2SeqSequenceClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size,)`, *optional*):
            Labels for computing the sequence classification/regression loss. Indices should be in `[0, ...,
            config.num_labels - 1]`. If `config.num_labels > 1` a classification loss is computed (Cross-Entropy).
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if labels is not None:
            use_cache = False

        if input_ids is None and inputs_embeds is not None:
            raise NotImplementedError(
                f"Passing input embeddings is currently not supported for {self.__class__.__name__}"
            )

        outputs = self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            head_mask=head_mask,
            decoder_head_mask=decoder_head_mask,
            cross_attn_head_mask=cross_attn_head_mask,
            encoder_outputs=encoder_outputs,
            inputs_embeds=inputs_embeds,
            decoder_inputs_embeds=decoder_inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        hidden_states = outputs[0]  # last hidden state

        eos_mask = input_ids.eq(self.config.eos_token_id)

        if len(torch.unique_consecutive(eos_mask.sum(1))) > 1:
            raise ValueError(
                "All examples must have the same number of <eos> tokens.")
        sentence_representation = hidden_states[eos_mask, :].view(hidden_states.size(0), -1, hidden_states.size(-1))[
            :, -1, :
        ]
        logits = self.classification_head(sentence_representation)

        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.config.num_labels == 1:
                    self.config.problem_type = "regression"
                elif self.config.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int):
                    self.config.problem_type = "single_label_classification"
                else:
                    self.config.problem_type = "multi_label_classification"

            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.config.num_labels == 1:
                    loss = loss_fct(logits.squeeze(), labels.squeeze())
                else:
                    loss = loss_fct(logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(
                    logits.view(-1, self.config.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(logits, labels)
        if not return_dict:
            output = (logits,) + outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return Seq2SeqSequenceClassifierOutput(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            decoder_hidden_states=outputs.decoder_hidden_states,
            decoder_attentions=outputs.decoder_attentions,
            cross_attentions=outputs.cross_attentions,
            encoder_last_hidden_state=outputs.encoder_last_hidden_state,
            encoder_hidden_states=outputs.encoder_hidden_states,
            encoder_attentions=outputs.encoder_attentions,
        )


def load_llm_model(model_directory: str):
    tokenizer = AutoTokenizer.from_pretrained(
        "impira/layoutlm-document-qa",
        add_prefix_space=True,
    )
    pipeline = pipeline(
        model="impira/layoutlm-document-qa",
        tokenizer=tokenizer,
        trust_remote_code=True,
    )
    return pipeline


def load_seq_model(model_directory: str) -> tuple[RobertaForQuestionAnsweringWithNegatives, BartTokenizerFast]:
    if (model_directory / "seq_model").exists():
        print("Fine tuned Sequence Classifier model found, loading...")
        tokenizer = BartTokenizerFast.from_pretrained(
            "facebook/bart-large-mnli")
        model = BartForSequenceClassificationWithNegatives.from_pretrained(
            model_directory / "seq_model")
    else:
        print("No fine tuned Sequence Classifier model found, loading generic model...")
        tokenizer = BartTokenizerFast.from_pretrained(
            "facebook/bart-large-mnli")
        model = BartForSequenceClassificationWithNegatives.from_pretrained(
            "facebook/bart-large-mnli")
    return model, tokenizer


class LayoutLMLabellingFunction(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)

    def load(self, model_directory: Path, device: Union[int, str]) -> None:
        self.device = device
        self.model_directory = model_directory
        self.vqa_model = load_llm_model(model_directory)
        self.seq_model, self.seq_tokenizer = load_seq_model(model_directory)
        self.classifier = pipeline(
            task='zero-shot-classification',
            model=self.seq_model,
            tokenizer=self.seq_tokenizer,
            device=device
        )

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        questions = self.get_schema("questions", variable_name)
        categories = self.get_schema("categories", variable_name)

    def train(self, data: dict[str, List["Extraction"]]):
        pass

    @property
    def labelling_method(self) -> str:
        return "Q&A → NLI Transformer"
