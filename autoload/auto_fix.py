#!/usr/bin/env python3

import difflib
import json
import yaml
import sys

WORD_LIST_MAP = {}


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def compare_and_replacer(
        input_word: str, word_list, th: float) -> str:
    if len(input_word) < 3:
        return input_word
    val = 0.0
    ret = input_word
    for words in word_list:
        if len(words) == 0:
            continue
        base_word = words[0]
        for word in words:
            tmp_val = similar(input_word, word)
            if tmp_val > th and tmp_val > val:
                val = tmp_val
                ret = base_word
    # NOTE: if converted word start with input word, input word has high
    # priority
    # if ret.startswith(input_word):
        # return input_word
    return ret


def vim_auto_fix_add_data(filetype, word, words=[]):
    if filetype in WORD_LIST_MAP:
        WORD_LIST_MAP[filetype] = []
    WORD_LIST_MAP[filetype] += [word] + words
    return True


def vim_auto_fix_dump(data_filepath):
    if data_filepath == '':
        print("[ERROR]: filepath is empty", file=sys.stderr)
        return False
    with open(data_filepath, 'w') as f:
        if data_filepath.endswith('.json'):
            json.dump(
                WORD_LIST_MAP,
                f,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                separators=(
                    ',',
                    ': '))
        elif data_filepath.endswith('.yaml'):
            yaml.dump(WORD_LIST_MAP, f, default_flow_style=False)
        else:
            print(
                "[ERROR]: invalid filetype: required json or yaml format",
                file=sys.stderr)
            return False
    return True


def vim_auto_fix_auto_word_fix(
        line: str, filetype='_', th=0.7, data_filepath: str = ''):
    if data_filepath == '':
        print("[ERROR]: filepath is empty", file=sys.stderr)
        return line
    global WORD_LIST_MAP
    if not WORD_LIST_MAP:
        with open(data_filepath) as f:
            if data_filepath.endswith('.json'):
                WORD_LIST_MAP = json.load(f)
            elif data_filepath.endswith('.yaml'):
                WORD_LIST_MAP = yaml.load(f)
            else:
                print(
                    "[ERROR]: invalid filetype: required json or yaml format",
                    file=sys.stderr)
                return line
    if '_' not in WORD_LIST_MAP:
        print("[ERROR]: '_' filetype not found", file=sys.stderr)
        return line
    if filetype not in WORD_LIST_MAP:
        # print("[WARN]: '{}' filetype not found".format(filetype), file=sys.stderr)
        WORD_LIST_MAP[filetype] = []
    word_list = WORD_LIST_MAP['_'] + WORD_LIST_MAP[filetype]
    newline = compare_and_replacer(line, word_list, th)
    # newline = ' '.join([compare_and_replacer(x, word_list, th) for x in line.split(' ')])
    return newline


# def main():
    # line = sys.argv[1]
    # newline = vim_auto_fix_auto_word_fix(line, 'c')
    # print(newline)
