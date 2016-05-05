# encoding=utf-8


"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""

from langconv import *



# from fanti -> jianti
line="繁体简体转换蘩車門"
line = Converter('zh-hans').convert(line.decode('utf-8'))
line = line.encode('utf-8')
print line
 
# jianti->fanti
line = Converter('zh-hant').convert(line.decode('utf-8'))
line = line.encode('utf-8')
print line







