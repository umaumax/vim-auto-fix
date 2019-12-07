#!/usr/bin/env python3

import difflib
import json
import sys

WORD_LIST_MAP = {}


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def compare_and_replacer(input_word, word_list, th):
    if len(input_word) < 3:
        return input_word
    val = 0.0
    ret = input_word
    for word in word_list:
        tmp_val = similar(input_word, word)
        if tmp_val > th and tmp_val > val:
            val = tmp_val
            ret = word
    return ret


def vim_auto_fix_add_data(filetype, word):
    if filetype in WORD_LIST_MAP:
        WORD_LIST_MAP[filetype] = []
    WORD_LIST_MAP[filetype] += word
    return True


def vim_auto_fix_dump(data_filepath):
    if data_filepath == '':
        print("[ERROR]: filepath is empty", file=sys.stderr)
        return False
    with open(data_filepath, 'w') as f:
        WORD_LIST_MAP = json.load(f)
        json.dump(
            WORD_LIST_MAP,
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            separators=(
                ',',
                ': '))
    return True


def vim_auto_fix_auto_word_fix(
        line, filetype='_', th=0.7, data_filepath=''):
    if data_filepath == '':
        print("[ERROR]: filepath is empty", file=sys.stderr)
        return line
    global WORD_LIST_MAP
    if not WORD_LIST_MAP:
        with open(data_filepath) as f:
            WORD_LIST_MAP = json.load(f)
    if not '_' in WORD_LIST_MAP:
        print("[ERROR]: '_' filetype not found", file=sys.stderr)
        return line
    if not filetype in WORD_LIST_MAP:
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
