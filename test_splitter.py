# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
from pprint import pprint
from splitter import SentenceSplitter

class TestSplitter(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test_number = 0
        self.en_splitter = SentenceSplitter('en')
        #self.en_splitter = SentenceSplitter('en')

    def testSimpleEng(self):
        text_src = 'Mr Dursley was the director. Of a firm called . Grunnings, which made drills.'
        text_exp = 'Mr Dursley was the director.\nOf a firm called .\nGrunnings, which made drills.\n'
        res = self.en_splitter.process_string(text_src)
        self.assertEqual(res, text_exp)

    def testNonBreakingChar(self):
        text_src = 'Mr. Dursley was the director. Of a firm called .'
        text_exp = 'Mr. Dursley was the director.\nOf a firm called .\n'
        res = self.en_splitter.process_string(text_src)
        self.assertEqual(res, text_exp)

    def testQuotes(self):
        text_src = '"William Crosby, why, what brings you out in such a storm as this? Strip off your coat, and draw up to the fire, can\'t ye?"'
        text_exp = '"William Crosby, why, what brings you out in such a storm as this?\nStrip off your coat, and draw up to the fire, can\'t ye?"\n'
        res = self.en_splitter.process_string(text_src)
        self.assertEqual(res, text_exp)

    def testKorean(self):
        text_src = '1년 만에 완전체로. 돌아온 크레용팝의. 두 번째 미니앨범 ‘FM’!'
        text_exp = ''
        res = self.en_splitter.process_string(text_src)
        self.assertEqual(res, text_exp)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSplitter)
    unittest.TextTestRunner(verbosity=2).run(suite)