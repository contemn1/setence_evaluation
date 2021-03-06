import numpy as np
from torch.utils.data import Dataset
import torch


class TextIndexDataset(Dataset):
    def __init__(self, word_sequence, tokenizer,
                 use_cuda=False, max_length=64):
        self.raw_texts = word_sequence
        self.tokenizer = tokenizer
        self.use_cuda = use_cuda
        self.max_length = max_length

    def __len__(self):
        return len(self.raw_texts)

    def __getitem__(self, index):
        tokens = self.tokenizer.tokenize(self.raw_texts[index])[:self.max_length]
        new_tokens = ["[CLS]"] + tokens
        new_tokens.append("[SEP]")
        return new_tokens

    def collate_fn_one2one(self, batch_sents):
        '''
        Puts each data field into a tensor with outer dimension batch size"
        '''
        bert_ids = [self.tokenizer.convert_tokens_to_ids(tokens) for tokens in batch_sents]
        sequence_lengths = np.array([len(ele) for ele in bert_ids])
        padded_batch_ids = pad(bert_ids, sequence_lengths,
                               0)  # type: torch.Tensor
        input_masks = padded_batch_ids > 0
        return padded_batch_ids, input_masks


def pad(sequence_raw, sequence_length, pad_id):
    def pad_per_line(index_list, max_length):
        return np.concatenate(
            (index_list, [pad_id] * (max_length - len(index_list))))

    max_seq_length = np.max(sequence_length)
    padded_sequence = np.array(
        [pad_per_line(x_, max_seq_length) for x_ in sequence_raw],
        dtype=np.int64)

    padded_sequence = torch.from_numpy(padded_sequence)

    return padded_sequence

