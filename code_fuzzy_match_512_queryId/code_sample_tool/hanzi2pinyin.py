#!/usr/bin/env python
# encoding=utf-8





from xpinyin import Pinyin
p = Pinyin()

word='7寿'
word='寿宝庄'
word=unicode(word,'utf-8')
ping=p.get_pinyin(word,' ')
print ping,ping.split(' ')
