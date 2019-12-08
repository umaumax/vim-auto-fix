#!/usr/bin/env python3

import unittest

import auto_fix


class FizzBuzzTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_vim_auto_fix_add_data_normal(self):
        ret = auto_fix.vim_auto_fix_add_data(
            './test.yaml', 'test', 'abc', ['abc2'])
        self.assertEqual(ret, True)
        self.assertEqual(auto_fix.WORD_LIST_MAP['test'], [['abc', 'abc2']])


if __name__ == "__main__":
    unittest.main()
