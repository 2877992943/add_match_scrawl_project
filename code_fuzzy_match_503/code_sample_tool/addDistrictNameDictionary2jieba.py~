#!/usr/bin/env python
#encoding=utf-8
"""add dictionary temporally"""
#from __future__ import print_function, unicode_literals
import sys
#sys.path.append("../")
import jieba
#jieba.load_userdict("userdict.txt")
#import jieba.posseg as pseg


def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)

def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()






#############load district dict
districtNameList=grab('/home/yr/intellicredit/data/'+'districtNameList0503')
 



test_sent = [
"李小福是创新办主任也是云计算方面的专家; 什么是八一双鹿,上海市浦东区\n"
]

######## print cut before add dictionary
print test_sent[0].decode('utf-8')
words = jieba.cut(test_sent[0].decode('utf-8'))
print('/'.join(words))




####add word_dictionary to jieba
for w in districtNameList[:]:
	#print w
	jieba.add_word(w)
####add district-name-not-in-dictionary to jieba
jieba.add_word('浦东区')


words = jieba.cut(test_sent[0].decode('utf-8'))
print('/'.join(words))

 
