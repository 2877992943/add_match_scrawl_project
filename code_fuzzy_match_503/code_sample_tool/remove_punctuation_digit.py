#!/usr/bin/env python
# encoding=utf-8



import re


temp = "想做/ 兼_职/学生_/ 的 、加,我Q：  1 5.  8 0. ！！？？  8 6 。0.  2。 3     有,惊,喜,哦"
temp = temp.decode("utf8")
string = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),temp)
print string


####
temp=string
string = re.sub("[ \f\r\t\n\w]+".decode("utf8"), "".decode("utf8"),temp)
string=[w for w in string if w not in ["：".decode("utf8")]]
for w in string:
    print w