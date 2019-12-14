#!/usr/bin/env python3

import re
import difflib
import json
import yaml
import sys
import os

import typodistance

WORD_LIST_MAP = {}

AUTO_FIX_DEBUG = ''


def difflib_similar(base: str, input: str):
    return difflib.SequenceMatcher(None, base, input).ratio()


def typodistance_similar(base: str, input: str):
    base_score = 10.0
    if base == input:
        return base_score
    common_prefix_length = len(typodistance.commonprefix([base, input]))
    if common_prefix_length >= len(base):
        return 0.0

    dist = (typodistance.typoDistance(base, input) / len(base))
    # NOTE: for debug only
    global AUTO_FIX_DEBUG
    if not AUTO_FIX_DEBUG:
        AUTO_FIX_DEBUG = os.environ.get('AUTO_FIX_DEBUG', '0')
    if AUTO_FIX_DEBUG != '0':
        print("[typodistance_similar] base:{}, input:{}, dist:{}, common_prefix_length:{}".format(
            base, input, dist, common_prefix_length))
    if dist < 0.8 and common_prefix_length >= 3:
        # NOTE: to set priority among other word
        return base_score - dist
    return 0.0


def compare_and_replacer(
        input_word: str, word_lists, th: float) -> str:
    if len(input_word) < 3:
        return input_word
    val = 0.0
    ret = input_word
    for words in word_lists:
        if len(words) == 0:
            continue
        base_word = words[0]
        for word in words:
            tmp_val = typodistance_similar(word, input_word)
            if tmp_val > th and tmp_val > val:
                val = tmp_val
                ret = base_word
    # NOTE: if converted word start with input word, input word has high
    # priority
    # if ret.startswith(input_word):
        # return input_word
    return ret


def vim_auto_fix_add_data(
        data_filepath: str, filetype: str, word: str, words=[]) -> bool:
    if not vim_auto_fix_init_word_list_map(data_filepath):
        return False
    if filetype not in WORD_LIST_MAP:
        WORD_LIST_MAP[filetype] = []
    WORD_LIST_MAP[filetype] += [[word] + words]
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


def vim_auto_fix_init_word_list_map(data_filepath: str) -> bool:
    global WORD_LIST_MAP
    if not WORD_LIST_MAP:
        with open(data_filepath) as f:
            if data_filepath.endswith('.json'):
                WORD_LIST_MAP = json.load(f)
            elif data_filepath.endswith('.yaml'):
                WORD_LIST_MAP = yaml.load(f, Loader=yaml.SafeLoader)
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
    if not vim_auto_fix_init_word_list_map(data_filepath):
        return word
    if '_' not in WORD_LIST_MAP:
        print("[ERROR]: '_' filetype not found", file=sys.stderr)
        return word
    if filetype not in WORD_LIST_MAP:
        # print("[WARN]: '{}' filetype not found".format(filetype), file=sys.stderr)
        WORD_LIST_MAP[filetype] = []
    word_list = WORD_LIST_MAP['_'] + WORD_LIST_MAP[filetype]

    # NOTE: extract word
    # #inclue -> # inclue -> # include -> #inlcude
    # 「hot🔥dog🐶」 -> ['', '「', 'hot', '🔥', 'dog', '🐶」']
    line_words = re.findall(r'[a-zA-Z_]+|[^a-zA-Z_]+', word)
    for (i, word) in enumerate(line_words):
        if re.match(r'^[a-zA-Z_]+$', word):
            newword = compare_and_replacer(word, word_list, th)
            line_words[i] = newword
    return ''.join(line_words)


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
