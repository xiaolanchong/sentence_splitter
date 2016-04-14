# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
from pprint import pprint
import splitter


class TestSplitter(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test_number = 0

    def testSimple(self):
        text_src = 'Mr Dursley was the director. Of a firm called . Grunnings, which made drills.'
        text_exp = 'Mr Dursley was the director.\nOf a firm called .\nGrunnings, which made drills.\n'
        res = splitter.process_string(text_src)
        self.assertEqual(res, text_exp)

    def testNonBreakingChar(self):
        text_src = 'Mr. Dursley was the director. Of a firm called .'
        text_exp = 'Mr. Dursley was the director.\nOf a firm called .\n'
        res = splitter.process_string(text_src)
        self.assertEqual(res, text_exp)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSplitter)
    unittest.TextTestRunner(verbosity=2).run(suite)