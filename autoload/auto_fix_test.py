#!/usr/bin/env python3

import os
import unittest

import auto_fix


class FizzBuzzTest(unittest.TestCase):
    def setUp(self):
        os.environ['AUTO_FIX_DEBUG'] = '1'

    def tearDown(self):
        pass

    def test_vim_auto_fix_add_data_normal(self):
        ret = auto_fix.vim_auto_fix_add_data(
            './test.yaml', 'test', 'abc', ['abc2'])
        self.assertEqual(ret, True)
        self.assertEqual(auto_fix.WORD_LIST_MAP['test'], [['abc', 'abc2']])

    def test_vim_auto_fix_compare_and_replacer_normal(self):
        base_word = 'sample'
        word_lists = [['sample']]
        inputs = ['sample', 'sampel', 'samplw', 'sampl']
        for input in inputs:
            ret = auto_fix.compare_and_replacer(input, word_lists, th=0.8)
            self.assertEqual(ret, base_word)

    def test_vim_auto_fix_compare_and_replacer_error(self):
        base_word = 'sample'
        word_lists = [['sample']]
        inputs = ['samples']
        for input in inputs:
            ret = auto_fix.compare_and_replacer(input, word_lists, th=0.8)
            self.assertNotEqual(ret, base_word, "at input:'{}'".format(input))


if __name__ == "__main__":
    unittest.main()
