from models import BLSTMEncoder
import numpy as np
import logging
import json
import sys
import torch
from sklearn.metrics.pairwise import cosine_similarity
from IOUtil import get_word_dict
from IOUtil import get_glove
from nltk.tokenize import word_tokenize

DATA_PATH = "/home/zxj/Downloads/data"
GLOVE_PATH = DATA_PATH + "/glove.840B.300d.txt"


def load_sentences(file_path):
    try:
        with open(file_path, encoding="utf8") as file:
            sentence_dict = [json.loads(line) for line in file]
            return sentence_dict
    except IOError as err:
        logging.error("Failed to open file {0}".format(err))
        sys.exit(1)


def read_file(file_path, preprocess=lambda x: x):
    try:
        with open(file_path, encoding="utf8") as file:
            for sentence in file.readlines():
                yield (preprocess(sentence))

    except IOError as err:
        logging.error("Failed to open file {0}".format(err))
        sys.exit(1)


def resume_model(model_path, glove_path=GLOVE_PATH, use_cuda=False):
    location_function = None if use_cuda else lambda storage, loc: storage
    model = torch.load(model_path, map_location=location_function)  # type: BLSTMEncoder
    model.set_glove_path(glove_path)
    model.build_vocab_k_words(K=100000)
    return model


def encoding_setences(model_path, glove_path, sentence_list, use_cuda=False) -> np.ndarray:
    model = resume_model(model_path, glove_path,use_cuda)  #type: BLSTMEncoder
    embeddings = model.encode(sentence_list, bsize=128, tokenize=True, verbose=True)
    return embeddings


def output_encoding():
    model_path = DATA_PATH + "/infersent.allnli.pickle"
    setence_embeddings = encoding_setences(model_path)
    output_path = DATA_PATH + "/infer-sent-embeddings-test"
    np.save(output_path, setence_embeddings)


def calculate_pairwise_similarity(embd):
    embd = embd.reshape((-1, 3, embd.shape[1]))
    for ele in embd:
        res_mat = cosine_similarity(ele)
        res_need = [str(res_mat[0][1].item()), str(res_mat[1][2].item()), str(res_mat[0][2].item())]
        print("\t".join(res_need))


def sentences_unfold(file_path, delimiter="\001"):
    sent_list = read_file(file_path, preprocess=lambda ele: ele.split(delimiter))
    sent_list = [arr for arr in sent_list if len(arr) == 3]
    sent_list = [ele for arr in sent_list for ele in arr]
    return sent_list


def load_sick(sick_path="/Users/zxj/Downloads/SICK/SICK.txt"):
    file_list = read_file(sick_path)
    file_list = (ele.split("\t")[1:7] for ele in file_list if not ele.startswith("pair_ID"))
    file_list = ([ele[0], ele[1], ele[3]] for ele in file_list if ele[2] == "ENTAILMENT")
    return file_list


def encode_sick(use_cuda):
    file_list = load_sick()
    file_list = list(file_list)
    first = [ele[0] for ele in file_list]
    second = [ele[1] for ele in file_list]
    third = [ele[2] for ele in file_list]
    model_path = "/Users/zxj/Downloads/sentence_evaluation/InferSent/encoder/infersent.allnli.pickle"
    model = resume_model(model_path, use_cuda=use_cuda)
    first_emb = model.encode(first, bsize=128, tokenize=True, verbose=True)
    second_emb = model.encode(second, bsize=128, tokenize=True, verbose=False)
    res = cosine_similarity(first_emb, second_emb).diagonal().tolist()
    for ele in zip(res, third):
        print(str(ele[0]) + "\t" + ele[1])


if __name__ == '__main__':
    file_path = "result.txt"
    model_path = "/Users/zxj/Downloads/sentence_evaluation/InferSent/encoder/infersent.allnli.pickle"
    glove_path = "/Users/zxj/Downloads/glove.840B.300d.txt"
    sentences = sentences_unfold(file_path)
    print(sentences[0])
    word_dict = get_word_dict(sentences)
    glove_dict = get_glove(GLOVE_PATH, word_dict)
    sentences = [word_tokenize(sent) for sent in sentences]
    sentences = [np.mean([glove_dict[word] for word in sent if word in glove_dict], axis=0) for sent in sentences]
    sentences = np.array(sentences)
    calculate_pairwise_similarity(sentences)