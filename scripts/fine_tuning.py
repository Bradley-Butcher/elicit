import json
from pathlib import Path
from typing import Tuple
from spacy import load
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, Trainer, TrainingArguments
import torch
import collections

model_name = "deepset/roberta-base-squad2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)


def read_squad(path: Path):
    """
    Function to read squad json file - taken from: https://huggingface.co/transformers/custom_datasets.html#qa-squad
    """
    path = Path(path)
    with open(path, 'rb') as f:
        squad_dict = json.load(f)

    contexts = []
    questions = []
    answers = []
    for group in squad_dict['data']:
        for passage in group['paragraphs']:
            context = passage['context']
            for qa in passage['qas']:
                question = qa['question']
                for answer in qa['answers']:
                    contexts.append(context)
                    questions.append(question)
                    answers.append(answer)

    return contexts, questions, answers


def add_end_idx(answers, contexts):
    """
    Function to add end_idx to answers dict.
    """
    for answer, context in zip(answers, contexts):
        gold_text = answer['text']
        start_idx = answer['answer_start']
        end_idx = start_idx + len(gold_text)

        # sometimes squad answers are off by a character or two – fix this
        if context[start_idx:end_idx] == gold_text:
            answer['answer_end'] = end_idx
        elif context[start_idx-1:end_idx-1] == gold_text:
            answer['answer_start'] = start_idx - 1
            # When the gold label is off by one character
            answer['answer_end'] = end_idx - 1
        elif context[start_idx-2:end_idx-2] == gold_text:
            answer['answer_start'] = start_idx - 2
            # When the gold label is off by two characters
            answer['answer_end'] = end_idx - 2


def add_token_positions(encodings, answers):
    """
    Convert character positions to token positions.
    """
    start_positions = []
    end_positions = []
    for i in range(len(answers)):
        start_positions.append(encodings.char_to_token(
            i, answers[i]['answer_start']))
        end_positions.append(encodings.char_to_token(
            i, answers[i]['answer_end'] - 1))

        # if start position is None, the answer passage has been truncated
        if start_positions[-1] is None:
            start_positions[-1] = tokenizer.model_max_length
        if end_positions[-1] is None:
            end_positions[-1] = tokenizer.model_max_length

    encodings.update({'start_positions': start_positions,
                     'end_positions': end_positions})


class QADataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings.input_ids)


def load_dataset(train_path: Path, test_path: Path) -> Tuple[QADataset, QADataset]:
    """
    Given a train and test path, return a train and test pytorch dataset object ready for training.
    """
    train_contexts, train_questions, train_answers = read_squad(train_path)
    val_contexts, val_questions, val_answers = read_squad(test_path)
    add_end_idx(train_answers, train_contexts)
    add_end_idx(val_answers, val_contexts)
    train_encodings = tokenizer(
        train_contexts, train_questions, truncation=True)
    val_encodings = tokenizer(
        val_contexts, val_questions, truncation=True)
    add_token_positions(train_encodings, train_answers)
    add_token_positions(val_encodings, val_answers)
    return QADataset(train_encodings), QADataset(val_encodings)


def tune(
        train_dataset: QADataset,
        test_dataset: QADataset,
        output_path: Path,
        log_path: Path,
        num_train_epochs: int = 4,
        batch_size: int = 5,
):
    training_args = TrainingArguments(
        output_dir=output_path,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=log_path,
        logging_steps=10,
        evaluation_strategy="epoch"
    )

    trainer = Trainer(model=model,
                      args=training_args,
                      train_dataset=train_dataset,
                      eval_dataset=test_dataset)

    trainer.train()
    trainer.save_model()


if __name__ == "__main__":
    train_path = Path(__file__).parent.parent / \
        'data' / 'labelled' / 'training.json'
    test_path = Path(__file__).parent.parent / \
        'data' / 'labelled' / 'testing.json'
    model_path = Path(__file__).parent.parent / "models"
    log_path = Path(__file__).parent.parent / "models" / "logs"
    train_data, test_data = load_dataset(train_path, test_path)
    tune(train_dataset=train_data, test_dataset=test_data,
         log_path=log_path, output_path=model_path)
