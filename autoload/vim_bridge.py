#!/usr/bin/env python3

import vim
import os

import auto_fix

DATA_FILEPATH = os.path.expanduser('~/.config/auto_fix/fix.json')


def vim_auto_bridge_fix_add_data(filetype, word):
    vim_auto_fix_add_data(filetype, word)


def vim_auto_fix_bridge_dump(data_filepath=DATA_FILEPATH):
    vim_auto_fix_dump(data_filepath)


def vim_auto_fix_bridge_auto_fix(
        input, filetype='_', data_filepath=DATA_FILEPATH):
    if not os.path.isfile(data_filepath):
        log = "[vim-auto-fix][ERROR]: no such file {}".format(data_filepath)
        vim.command('echohl ErrorMsg | echo "' + log + '" | echohl None')
        return input
    return vim_auto_fix_auto_word_fix(
        input, filetype, data_filepath=data_filepath)
