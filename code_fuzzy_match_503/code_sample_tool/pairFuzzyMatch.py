#!/usr/bin/env python
# encoding=utf-8

"""pair match:hanzi pinyin 4 score, get average score """

from fuzzywuzzy import fuzz


s1='北京 海淀 '
s2='北京市 海淀区'
s3='北京市 西城区'
s='亚运村 北京市 博耀 科技 有限公司'
#s1='beijing haidian'
#s2='beijingshi haidianqu'

score1=fuzz.token_sort_ratio(s,s)
score2=fuzz.partial_ratio(s,s)
print score1,score2

