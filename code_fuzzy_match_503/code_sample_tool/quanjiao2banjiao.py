#!/usr/bin/env python
# encoding=utf-8



"""http://www.cnblogs.com/kaituorensheng/p/3554571.html

中文全角　　，。、；‘？：“
中文半角　　，。、：”？；’
英文全角    ，．／；＇？：＂　　　   
英文半角　　 ,./;'?:"
"""
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""



"""# -*- coding: cp936 -*-"""
def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                              #全角空格直接转换            
            inside_code = 32 
        elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring
    
def strB2Q(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 32:                                 #半角空格直接转化                  
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:        #半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += unichr(inside_code)
    return rstring


#####################333
codeform='cp936'
codeform='utf-8'

raw="ｍｎ123abc博客园，。、；‘？：“ ，．／；＇？：＂"
b = strQ2B(raw.decode(codeform))                           
print b

c = strB2Q(raw.decode(codeform))                           
print c




