#!/usr/bin/env python
# encoding=utf-8


"""segment,do not remove single word, use forward/backward_pair to match, do not keep len=1 word in sentence"""

import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re,jieba,copy
import numpy as np

def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)

def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()


def cut_sentence_deep(sentence,deep):

    #sentence="北京市西城区西交民苑50号,上海市浦东区,上海浦东,上海浦东区,上海市浦东新区"
    if deep==True:
        line=jieba.cut_for_search(sentence)#for generate index
    else:line=jieba.cut(sentence)

    rst=' '.join(line)
    #print rst,len(rst)
    #rst=rst.split(' ')
    #print rst
    return rst


def addDictToJieba():
    ##### roadList
    content=open('../data_crawl/finalRoads.txt','r').read().strip('\n')
    contentList=content.split('\n');print len(contentList)
    #############load district dict
    districtNameList=grab('/home/yr/intellicredit/data/'+'districtNameList0503')
    test_sent = [
    "李小福是创新办主任也是云计算方面的专家; 什么是八一双鹿,上海市浦东区\n"
    ]
    ######## print cut before add dictionary
    #print test_sent[0].decode('utf-8')
    words = jieba.cut(test_sent[0].decode('utf-8'))
    #print('/'.join(words))

    ####add word_dictionary to jieba
    for w in districtNameList[:]+contentList:
	    #print w
	    jieba.add_word(w)
        ####add district-name-not-in-dictionary to jieba
    jieba.add_word('浦东区');
    jieba.add_word('浦东新区')
    jieba.del_word('上海市')
    jieba.add_word('兰城路')



    words = jieba.cut(test_sent[0].decode('utf-8'))
    #print('/'.join(words))


def complementDistrict(strI,briefNameDic):#string dict {briefName:completeName,...}
    strIII=copy.copy(strI)
    for bfname,completeName in briefNameDic.items():
        if bfname in strI or completeName in strI:
            #print strI[:3]

            #print bfname,completeName
            #strII=strI.replace(completeName,bfname)#上海上海市市浦东新区 get stem of word first  上海南汇区->上 海南省 汇区
            strIII=strII.replace(bfname,completeName) #strI remain, strII is updated



    return strIII

def get_briefDistrictName():
    districtNameBrief={}
    dataDic=grab('/home/yr/intellicredit/data/district_dict')
    for level1,v1 in dataDic.items()[:]:
        name=level1.strip(' ').decode('utf-8')
        nameBrief=name[:-1]
        districtNameBrief[nameBrief]=name
    return districtNameBrief


if __name__=="__main__":

    nameList=['address','companyName']
    fname=nameList[0]

    ####load jieba dict
    addDictToJieba()
    briefNameDic=get_briefDistrictName() #{briefName:name,...}
    ####load raw sentence
    fpath='../data_queryId/homeWorkAdd_id.csv'
    df=pd.read_csv(fpath, encoding="utf-8")[:]
    print df.columns
    queryId_arr=df['id'].values #array
    homeWorkAdd_arr=df['address'].values
    print queryId_arr.shape,homeWorkAdd_arr.shape# not use dict ,queryId repeat for homeAdd workAdd


    ####### start cut
    segmented=[];segmentedDeepList=[];queryIdList=[];rawList=[]
    #for line in df[:]:#1153
    for ind in range(queryId_arr.shape[0])[:]:

        line=homeWorkAdd_arr[ind]##string
        query_idi=queryId_arr[ind]#str
        #print line
        #
        if line==-1 or line=='-1':continue
        #print line
        ## complete name
        #line=complementDistrict(line,briefNameDic)#fail, use string_not_seg to get district,briefnameDistrict
        seg_deep=cut_sentence_deep(line,deep=True)
        seg=cut_sentence_deep(line,deep=False)
        #print seg
        sz=[len(ch) for ch in seg.split(' ')];
        #print sz
        #seg_removeSingle=[ch for ch in seg.split(' ') if len(ch)>=2]# 7 days hotel is removed
        seg_removeSingle=seg.split(' ')#list

        if len(seg_removeSingle)>=1:
            newStr=' '.join(seg_removeSingle)
            #print newStr
            segmented.append(newStr)
            segmentedDeepList.append(seg_deep)
            queryIdList.append(query_idi)
            rawList.append(line)
        #####
        if ind%100000==0:print ind

    print 'seg',len(segmented)

    ###
    pd.DataFrame({fname+'_seg':segmented,fname+'_raw':rawList,fname+'_deepSeg':segmentedDeepList,'id':queryIdList}).\
        to_csv('../data_queryId/'+fname+'_segmented_deepcut.csv',index=False,encoding='utf-8')





















