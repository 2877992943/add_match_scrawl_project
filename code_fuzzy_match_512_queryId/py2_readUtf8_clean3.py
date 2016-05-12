#!/usr/bin/env python
# encoding=utf-8

import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re
import numpy as np


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

    """
    nameList=['homeAdd','workAdd','workname']
    fname=nameList[2]

    fname3='py3doc_queryId_homeAdd_workName_workAdd.txt'
    #############3
    headList=['id','homeAdd','workName','workAdd']
    addressFile='../data_queryId/'+fname3
    content=open(addressFile,'rb').readlines()
    tot=[];error=0;messCode={}
    print 'tot',len(content)
    totalRecordList=[]
    for line in content[:]:
        recordDic={'id':-1,'homeAdd':-1,'workAdd':-1,'workName':-1}
        #print 'raw0',[line]
        line=line.strip('u');lineList=line.split(',');#print 'linelist',lineList

        lineList=[att.replace('\t','').replace('\n','') for att in lineList]#queryid homeadd workname workadd
        if len(lineList)<=1:continue
        for attI in range(len(headList)):
            att_tmp=lineList[attI];#print headList[attI],lineList[attI]
            #print '0..',lineList,type(lineList),len(lineList)
            if type(att_tmp)==str and len(att_tmp)>=1:#what else?

                try:
                    codeForm='utf-8'
                    lineDecode=att_tmp.decode(codeForm);#print 'is unicode?0',isinstance(lineDecode,unicode) #true
                    #print 'raw1',lineDecode,[lineDecode]
                    lineDecode=fanti2jianti(lineDecode);#print 'raw2',lineDecode
                    lineDecode=strQ2B(lineDecode);#print 'raw3',lineDecode
                    #if lineDecode!='NULL': not work here
                    cln=remove_punct(lineDecode);#print 'raw4',cln
                    #cln.replace('NULL','')
                    cln=leaveHanziNumZimu(cln)
                    if len(cln)>=3 and cln!='NULL':
                        #tot.append(cln)
                        recordDic[headList[attI] ]=cln
                        #print 'preprocessed',codeForm,cln

                except:
                    error+=1
        ################
        totalRecordList.append(recordDic)
        if len(totalRecordList)%100000==0:print len(totalRecordList)/100000
    print 'zhongwen',len(totalRecordList),'fail decode',error

    ########
    queryIdList=[dic['id'] for dic in totalRecordList];print 'queryId unique',len(queryIdList),len(set(queryIdList))
    homeAddList=[dic['homeAdd'] for dic in totalRecordList]
    workNameList=[dic['workName'] for dic in totalRecordList]
    workAddList=[dic['workAdd'] for dic in totalRecordList]

    pd.DataFrame({headList[0]:queryIdList,headList[1]:homeAddList,headList[2]:workNameList,headList[3]:workAddList}).\
        to_csv('../data_queryId/'+'queryId_homeAdd_workName_workAdd'+'_clean2.csv',index=False,encoding='utf-8')



    """
    ##############
    # combine homeAdd workAdd
    filepath='../data_queryId/'+'queryId_homeAdd_workName_workAdd'+'_clean2.csv'
    df=pd.read_csv(filepath, encoding="utf-8")[:]
    print '1',df.columns
    #########
    df_homeAdd=df['homeAdd'].values[:];print df_homeAdd.shape#[80w,]
    df_workAdd=df['workAdd'].values
    df_queryId=df['id'].values

    df_add=np.concatenate((df_homeAdd,df_workAdd));print df_add.shape
    df_add_id=np.concatenate((df_queryId,df_queryId))
    pd.DataFrame({'id':df_add_id,'address':df_add}).\
        to_csv('../data_queryId/homeWorkAdd_id.csv',index=False,encoding='utf-8')









