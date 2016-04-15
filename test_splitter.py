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
        text_exp = '1년 만에 완전체로.\n돌아온 크레용팝의.\n두 번째 미니앨범 ‘FM’!\n'
        res = self.en_splitter.process_string(text_src)
        self.assertEqual(res, text_exp)

    def testChinese(self):
        text_src = '父亲说：“这得说说……” “是得说说。”娘说。说说，什么叫“说说”，说什么呢？'
        text_exp = '父亲说：“这得说说……” “是得说说。\n”娘说。\n说说，什么叫“说说”，说什么呢？\n'
        res = self.en_splitter.process_string(text_src)
        self.assertEqual(res, text_exp)

    def testJapanese(self):
        text_src = '『ハア。』と老女は當惑した樣に眼をしよぼつかせた。『無い筈はないでせう。尤も此邊では、戸籍上の名と家で呼ぶ名と違ふのがありますよ。』と、健は喙を容れた。'
        text_exp = '『ハア。\n』と老女は當惑した樣に眼をしよぼつかせた。\n『無い筈はないでせう。\n尤も此邊では、戸籍上の名と家で呼ぶ名と違ふのがありますよ。\n』と、健は喙を容れた。\n'
        res = self.en_splitter.process_string(text_src)
        #print(res)
        self.assertEqual(res, text_exp)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSplitter)
    unittest.TextTestRunner(verbosity=2).run(suite)