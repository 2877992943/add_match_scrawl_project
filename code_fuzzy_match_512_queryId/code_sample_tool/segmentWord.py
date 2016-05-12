#!/usr/bin/env python
# encoding=utf-8




import jieba

sentence="北京市西城区西交民苑50号"
sentence="甬酹姝)┺H笆18号2-3-2023"
line=jieba.cut(sentence,cut_all=False)
rst= ' '.join(line)
print rst,len(rst)
rst=rst.split(' ')
for w in rst:print w





