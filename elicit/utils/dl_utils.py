import torch
from torch.utils.data import Dataset
from sentence_transformers import InputExample


class QADataset(Dataset):
    def __init__(self, data_dict: dict[str, list], questions: dict[str, list], tokenizer):
        self.contexts = []
        self.questions = []
        self.answers = []
        for key, value in data_dict.items():
            for vi in value:
                qus = questions[key]
                self.contexts += [vi.wider_context] * len(qus)
                self.answers += [self.get_answer_start_end(
                    vi.validated_context, vi.wider_context)] * len(qus)
                self.questions += qus
        self.encodings = self.prepare_train_features(tokenizer)

    def get_answer_start_end(self, answer: str, context: str):
        """
        Extracts the start and end indices of the answer in the context.

        :param answer: The answer.
        :param context: The context.

        :return: The start and end indices.
        """
        answer_start = context.find(answer)
        answer_end = answer_start + len(answer)
        return {"answer_start": answer_start, "answer_end": answer_end}

    def prepare_train_features(self, tokenizer, pad_on_right: bool = True):
        # Some of the questions have lots of whitespace on the left, which is not useful and will make the
        # truncation of the context fail (the tokenized question will take a lots of space). So we remove that
        # left whitespace
        self.questions = [q.lstrip() for q in self.questions]

        # Tokenize our examples with truncation and padding, but keep the overflows using a stride. This results
        # in one example possible giving several features when a context is long, each of those features having a
        # context that overlaps a bit the context of the previous feature.
        tokenized_examples = tokenizer(
            self.questions if pad_on_right else self.contexts,
            self.contexts if pad_on_right else self.questions,
            truncation="only_second" if pad_on_right else "only_first",
            max_length=512,
            stride=128,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding="max_length",
        )

        # Since one example might give us several features if it has a long context, we need a map from a feature to
        # its corresponding example. This key gives us just that.
        sample_mapping = tokenized_examples.pop("overflow_to_sample_mapping")
        # The offset mappings will give us a map from token to character position in the original context. This will
        # help us compute the start_positions and end_positions.
        offset_mapping = tokenized_examples.pop("offset_mapping")

        # Let's label those examples!
        tokenized_examples["start_positions"] = []
        tokenized_examples["end_positions"] = []

        for i, offsets in enumerate(offset_mapping):
            # We will label impossible answers with the index of the CLS token.
            input_ids = tokenized_examples["input_ids"][i]
            cls_index = input_ids.index(tokenizer.cls_token_id)

            # Grab the sequence corresponding to that example (to know what is the context and what is the question).
            sequence_ids = tokenized_examples.sequence_ids(i)

            # One example can give several spans, this is the index of the example containing this span of text.
            sample_index = sample_mapping[i]
            answers = self.answers[sample_index]
            # If no answers are given, set the cls_index as answer.
            if answers["answer_start"] == None:
                tokenized_examples["start_positions"].append(cls_index)
                tokenized_examples["end_positions"].append(cls_index)
            else:
                # Start/end character index of the answer in the text.
                start_char = answers["answer_start"]
                end_char = answers["answer_end"]

                # Start token index of the current span in the text.
                token_start_index = 0
                while sequence_ids[token_start_index] != (1 if pad_on_right else 0):
                    token_start_index += 1

                # End token index of the current span in the text.
                token_end_index = len(input_ids) - 1
                while sequence_ids[token_end_index] != (1 if pad_on_right else 0):
                    token_end_index -= 1

                # Detect if the answer is out of the span (in which case this feature is labeled with the CLS index).
                if not (offsets[token_start_index][0] <= start_char and offsets[token_end_index][1] >= end_char):
                    tokenized_examples["start_positions"].append(cls_index)
                    tokenized_examples["end_positions"].append(cls_index)
                else:
                    # Otherwise move the token_start_index and token_end_index to the two ends of the answer.
                    # Note: we could go after the last offset if the answer is the last word (edge case).
                    while token_start_index < len(offsets) and offsets[token_start_index][0] <= start_char:
                        token_start_index += 1
                    tokenized_examples["start_positions"].append(
                        token_start_index - 1)
                    while offsets[token_end_index][1] >= end_char:
                        token_end_index -= 1
                    tokenized_examples["end_positions"].append(
                        token_end_index + 1)

        return tokenized_examples

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, idx):
        return {key: torch.tensor(value[idx]) for key, value in self.encodings.items()}


class SequenceDataset(Dataset):
    def __init__(self, data: list, categories: list, tokenizer) -> None:
        self.contexts = []
        self.categories = []
        for extraction in data:
            self.contexts += [extraction.wider_context]
            self.categories += [extraction.value]
        label_dict = {cat: i for i, cat in enumerate(set(categories))}
        self.labels = torch.tensor([label_dict[cat]
                                   for cat in self.categories])
        self.encodings = tokenizer(
            self.contexts, truncation=True, padding=True)

    def __getitem__(self, idx: int):
        item = {key: torch.tensor(val[idx])
                for key, val in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item

    def __len__(self):
        return len(self.labels)


def extraction_to_input_examples(extraction, questions: list, negative_val: float = 0.1) -> InputExample:
    label = 1.0 if extraction.valid else negative_val
    question_examples = [
        InputExample(
            texts=[
                context,
                question,
            ], label=label
        ) for question in questions
        for context in [extraction.local_context, extraction.exact_context]
    ]
    category_examples = [
        InputExample(
            texts=[
                context,
                extraction.value,
            ], label=label
        ) for context in [extraction.local_context, extraction.exact_context]
    ]
    return question_examples + category_examples
