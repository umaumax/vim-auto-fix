#!/usr/bin/env python3

import re
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
        word: str, filetype='_', th=0.7, data_filepath: str = ''):
    if data_filepath == '':
        print("[ERROR]: filepath is empty", file=sys.stderr)
        return word
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
                return word
    if '_' not in WORD_LIST_MAP:
        print("[ERROR]: '_' filetype not found", file=sys.stderr)
        return word
    if filetype not in WORD_LIST_MAP:
        # print("[WARN]: '{}' filetype not found".format(filetype), file=sys.stderr)
        WORD_LIST_MAP[filetype] = []
    word_list = WORD_LIST_MAP['_'] + WORD_LIST_MAP[filetype]

    # NOTE: extract word for #inclue -> # inclue -> # include -> #inlcude
    m = re.match(
        r'(?P<prefix>[^a-zA-Z_-]*)(?P<word>[a-zA-Z_-]*)(?P<suffix>[^a-zA-Z_-]*)',
        word)
    newword = compare_and_replacer(m.groupdict()['word'], word_list, th)
    return m.groupdict()['prefix'] + newword + m.groupdict()['suffix']


def main():
    import os
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-d',
        '--data-filepath',
        default=os.path.expanduser("~/.config/auto_fix/fix.yaml"))
    parser.add_argument('-f', '--filetype', default='_')
    parser.add_argument('word')
    parser.add_argument('args', nargs='*')  # any length of args is ok

    args, extra_args = parser.parse_known_args()

    newword = vim_auto_fix_auto_word_fix(
        args.word, args.filetype, data_filepath=args.data_filepath)
    print(newword)


if __name__ == '__main__':
    main()
