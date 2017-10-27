# -*- coding: utf-8 -*-

import sys
import logging
import json
import numpy as np
import configparser

def get_word_dict(sentences, tokenize=True):
    # create vocab of words
    word_dict = {}
    if tokenize:
        from nltk.tokenize import word_tokenize
    sentences = [s.split() if not tokenize else word_tokenize(s)
                 for s in sentences]
    for sent in sentences:
        for word in sent:
            if word not in word_dict:
                word_dict[word.lower()] = ''
    word_dict['<s>'] = ''
    word_dict['</s>'] = ''
    return word_dict


def get_glove(glove_path, word_dict):
    # create word_vec with glove vectors
    word_vec = {}
    with open(glove_path, encoding="utf8") as f:
        for line in f:
            word, vec = line.split(' ', 1)
            if word.lower() in word_dict:
                word_vec[word.lower()] = vec

    print('Found {0}(/{1}) words with glove vectors'.format(
                    len(word_vec), len(word_dict)))

    return word_vec


def load_numpy_arraies(file_path):
    return np.load(file_path)


def unfold_domain(text_list, keys=frozenset(["positive", "negative"])):
    sample_list = [[(index, text_dict[key].split(",")) for index, text_dict in enumerate(text_list)] for key in keys]

    all_tuples = []
    for sub_list in sample_list:
        for pair in sub_list:
            new_list = [(pair[0], ele.split("->")) for ele in pair[1]]
            all_tuples.extend(new_list)

    train_x = [tup for tup in all_tuples if len(tup[1]) > 1]
    train_y = [0] * len(sample_list[0]) + [1] * len(sample_list[1])
    return train_x, train_y


def output_list_to_file(file_path, output_list, process=lambda x: x):
    try:
        with open(file_path, mode="w+", encoding="utf-8") as file:
            for line in output_list:
                file.write(process(line))
                file.write("\n")
    except IOError as error:
        logging.error("Failed to open file {0}".format(error))


def read_configs(config_path):
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(config_path, encoding="utf-8")
    config_dict = {key: string_to_attributes(value) for key, value in config["arguments"].items()}
    return config_dict


def string_to_attributes(input_string):
    if input_string.lower() in {"yes", "true"}:
        return True
    if input_string.lower() in {"no", "false"}:
        return False

    if input_string.isdigit():
        return int(input_string)

    return input_string
