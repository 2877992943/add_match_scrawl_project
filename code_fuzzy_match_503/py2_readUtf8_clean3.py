#!/usr/bin/env python
# encoding=utf-8

import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re


def cut_sentence(sentence):
    import jieba

    #sentence="北京市西城区西交民苑50号"
    line=jieba.cut(sentence,cut_all=False)
    rst= ' '.join(line)
    #print rst,len(rst)
    rst=rst.split(' ')
    return rst


def remove_stopwords(sentence):
    stopwords=[]#tbd
    return 0



def remove_punct(word):
    ##
    punctList='& # , . ; :'.split(' ')
    for punct in punctList:
        word=word.replace(punct.decode('utf-8'),'')
    ##########
    word.strip('\n');word.strip('\t');word.strip(' ');
    word = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),word)
    word=word.replace('NULL','')

    return word

def is_chinese(uchar):
    def whetherInRange(uchar):
        if uchar>=u'\u4e00' and uchar<=u'\u9fa5':
            return True
        else:
            return False
    ################
    if isinstance(uchar,unicode)==False:
        uchar=uchar.decode('utf-8')
    ###################
    """whether unicode is chinese"""
    return whetherInRange(uchar)

def isNumberZimuHanzi(uchar):
    def whetherInRange(uchar):
        if uchar>=u'\u4e00' and uchar<=u'\u9fa5':#hanzi
            return True
        else:
            if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):#zimu
                return True
            else:
                if uchar >= u'\u0030' and uchar<=u'\u0039':#number
                    return True
                else:return False


    #####################
    if isinstance(uchar,unicode)==False:
        uchar=uchar.decode('utf-8')
    ####
    return whetherInRange(uchar)



def strQ2B(ustring):
    if isinstance(ustring,unicode)==False:
        ustring=ustring.decode('utf-8')
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



def fanti2jianti(line):
    #print 'is unicode?',isinstance(line,unicode) #true
    from langconv import *
    # from fanti -> jianti
    #line="繁体简体转换蘩車門"
    if isinstance(line,unicode)==False:#if not utf8 ->decode utf8
        line = Converter('zh-hans').convert(line.decode('utf-8'))
    else:
        line = Converter('zh-hans').convert(line)
    ##############3
    line = line.encode('utf-8')
    #print 'is unicode??',isinstance(line,unicode)#false
    return line



def leaveHanziNumZimu(string):

    StrNew=[];#print line
    for char in string:
        if isNumberZimuHanzi(char):StrNew.append(char)
    #############
    StrNew=''.join(StrNew);#print 'new',lineNewStr
    return StrNew




if __name__=="__main__":

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[2]


    #############3
    addressFile='../data/py3doc_'+fname+'.txt'
    content=open(addressFile,'rb').readlines()
    tot=[];error=0;messCode={}
    content=content[1:]
    for line in content[:]:
        #print 'raw0',[line]
        line=line.strip('u');line=line.replace('\n','')
        #print '0..',line,type(line),len(line)
        if type(line)==str and len(line)>=1:
        #if isinstance(line,str):
            try:
                codeForm='utf-8'
                lineDecode=line.decode(codeForm);#print 'is unicode?0',isinstance(lineDecode,unicode) #true
                #print 'raw1',lineDecode,[lineDecode]
                lineDecode=fanti2jianti(lineDecode);#print 'raw2',lineDecode
                lineDecode=strQ2B(lineDecode);#print 'raw3',lineDecode
                #if lineDecode!='NULL': not work here
                cln=remove_punct(lineDecode);#print 'raw4',cln
                #cln.replace('NULL','')
                cln=leaveHanziNumZimu(cln)
                if len(cln)>=3 and cln!='NULL':

                    tot.append(cln)
                    #print 'preprocessed',codeForm,cln




            except:
                error+=1
    print 'zhongwen',len(tot),'fail decode',error


    pd.DataFrame({fname: tot[:]}).\
        to_csv('../data/'+fname+'_clean2.csv',index=False,encoding='utf-8')

    """



    ###############
    #  for homeAddress only ,still messcode
    ############
    df=pd.read_csv('../data/'+fname+'_clean2.csv', encoding="utf-8")
    print df.columns,df.values.shape,df[df.columns[0]].values.shape #[n,1],[n,]
    string=df[df.columns[0]].values#dataframe->serial->array

    tot=[]
    for line in string[:]:#string
        lineNew=[];#print line
        for w in line: #for char in string
            #print w,isNumberZimuHanzi(w)
            if isNumberZimuHanzi(w):lineNew.append(w)
        #############
        lineNewStr=''.join(lineNew);#print 'new',lineNewStr
        tot.append(lineNewStr)

    ######

    pd.DataFrame({fname: tot[:]}).\
        to_csv('../data/'+fname+'_clean2.csv',index=False,encoding='utf-8')"""












