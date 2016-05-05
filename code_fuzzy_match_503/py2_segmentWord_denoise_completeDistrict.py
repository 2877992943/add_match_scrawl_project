#!/usr/bin/env python
# encoding=utf-8


"""segment,do not remove single word, use forward/backward_pair to match, do  keep len=1 word in sentence
1)get district,city etc structure from address,
2)remove noise like ( ) |first repeated word |number |appear in the end, not begaining of addresss"""

#import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re,jieba


def cut_sentence(sentence):

    #sentence="北京市西城区西交民苑50号"
    line=jieba.cut(sentence,cut_all=False)
    rst= ' '.join(line)
    #print rst,len(rst)
    #rst=rst.split(' ')
    return rst

def remove_noise(strList):
    noise0=['(',')','-']#whole address
    #zimu='a b c d e f'.split(' ')+'a b c d e f'.upper().split(' ')
    noise1=['弄','楼','层','号楼','号','幢','栋','单元','室','附近','（','）','?'] #whole address
    noise2=['一','二','三','四','五','六','七','八','九','十','零','首'] #behind half address 三楼 A座 三层 3F
    noise1=[i.decode('utf-8') for i in noise1]
    noise2=[i.decode('utf-8') for i in noise2]
    combine1=[i+j for i in noise2 for j in noise1[:-4]]# 三楼 三层
    #combine2=[i+j for i in zimu for j in ['座'.decode('utf-8')] ]#A座


    #### whole address
    #strList=[si for si in strList if si not in noise0+noise1+noise2+combine1+combine2]
    strList=[si for si in strList if si not in noise0+noise1+combine1]
    #####
    return strList
    """
    #### half address in the behind
    sz_half=int(len(strList)/2)
    firstHalfStr=strList[:sz_half]
    if sz_half <=1:return strList
    else:
        for si in strList[sz_half:]:#if szHalf=6 or 5
            if si not in noise1+noise2:firstHalfStr.append(si)
        return firstHalfStr
    """

def remove_noise_notsplit(string):
    #string=' '.join(strList)
    # 13楼

    #string=re.sub(r'[0-9]{1,4}[a-zA-Z]{1,5}',''.decode('utf-8'),string)
    string=re.sub(r'[0-9]{1,4}[f,F]',''.decode('utf-8'),string)#3F
    for char in ['弄','楼','层','号楼','号','幢','栋','单元','室','座']:
        string=re.sub(r'[0-9]{1,10}'+' '+char.decode('utf-8'),' '.decode('utf-8'),string) # '13 楼'
        string=re.sub(r'[a-zA-Z]{1,10}'+char.decode('utf-8'),''.decode('utf-8'),string) #   'a座'

    return string

def remove_repeat(strList): #beijing beijing appear 2 times

    uniqueStr=[]
    for strI in strList:
        if strI not in uniqueStr:uniqueStr.append(strI)
    return uniqueStr


def remove_digitString(strList): #not remove 301 醫院   7天
    #strList=[stri.lower().strip('f') for stri in strList] #do not change name of entity
    #=[stri.lower().strip('floor') for stri in strList]#only->nly
    if len(strList)==1 and strList[0].isdigit()==True:
        return []
    else:
        return strList

def is_chinese(uchar):
        """whether unicode is chniese"""
        if uchar >= u'u4e00' and uchar<=u'u9fa5':
                return True
        else:
                return False

def eachChar(string):
    for char in string:
        print char
        print is_chinese(char)


def get_briefDistrictName():
    districtNameBrief={}
    dataDic=grab('/home/yr/intellicredit/data/district_dict')
    for level1,v1 in dataDic.items()[:]:
        name=level1.strip(' ').decode('utf-8')
        nameBrief=name[:-1]
        districtNameBrief[nameBrief]=name
    return districtNameBrief
def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)

def complementDistrict(strI,briefNameDic):#list dict
    import copy
    strList=copy.copy(strI)
    for i in range(len(strI))[:2]:
        bfname=strI[i]
        if bfname in briefNameDic.keys():
            strList[i]=briefNameDic[bfname]
    return strList

def complementDistrict1(strI,briefNameDic):
    import copy
    strList=copy.copy(strI)
    for i in range(len(strI))[:3]:
        name=strI[i]
        #### each name
        for bfname,completename in briefNameDic.items():

            if bfname in name:
                name=name.replace(bfname,briefNameDic[bfname])
                strList[i]=name
    return strList









if __name__=="__main__":

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]

    ####df[df.columns[0]].values[:]
    df=pd.read_csv('../data/'+fname+'_segmented.csv',encoding='utf-8')

    ###
    col=df.columns;print col #seg raw
    segSerial=df[col[0]].values[:];print segSerial.shape
    rawSerial=df[col[1]].values
    segSerial_denoise=[]
    briefNameDic=get_briefDistrictName()
    for string in segSerial[:]: #'西四 路以'33728:33740
        #print 'raw',string
        #eachChar(string)
        #print 'u?',isinstance(string,unicode) #true
        string=remove_noise_notsplit(string);#print '1', string ->string

        strList=[st.strip(' ') for st in string.split(' ') if len(st.strip(' '))>=1];#print '2',strList#['abc','er'..]
        strList=remove_repeat(strList)
        strList=remove_digitString(strList);#print 'remove digit',' '.join(strI)  ->list
        strList=remove_noise(strList);#print 'remove noise',' '.join(strI)  ->list
        strList=complementDistrict(strList,briefNameDic) #->list
        strList=remove_repeat(strList);#print 'unique',' '.join(strI)  ->list

        if len(strList)>0:segSerial_denoise.append(' '.join(strList) )
        else:segSerial_denoise.append('')
    ####
    print len(segSerial_denoise),len(rawSerial)
    pd.DataFrame({fname:segSerial_denoise,fname+'_raw':rawSerial[:]}).\
        to_csv('../data/'+fname+'_segmentDenoise.csv',index=False,encoding='utf-8')



















