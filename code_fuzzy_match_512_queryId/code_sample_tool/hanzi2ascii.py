#!/usr/bin/env python
# encoding=utf-8



word='寿宝庄寿保庄护户沪';print 'word',word
wordu=word.decode('utf-8');print 'wordu',wordu
for w in wordu:
	asc=ord(w);print asc,w
