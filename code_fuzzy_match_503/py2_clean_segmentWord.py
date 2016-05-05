#!/usr/bin/env python
# encoding=utf-8


"""segment,do not remove single word, use forward/backward_pair to match, do not keep len=1 word in sentence"""

import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re,jieba,copy

def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)

def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()


def cut_sentence(sentence):

    #sentence="北京市西城区西交民苑50号,上海市浦东区,上海浦东,上海浦东区,上海市浦东新区"
    line=jieba.cut(sentence,cut_all=False)
    rst= ' '.join(line)
    #print rst,len(rst)
    #rst=rst.split(' ')
    #print rst
    return rst


def addDictToJieba():
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
    for w in districtNameList[:]:
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

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]

    ####
    addDictToJieba()
    briefNameDic=get_briefDistrictName() #{briefName:name,...}
    ####
    filepath='../data/'+fname+'_clean2.csv'
    df=pd.read_csv(filepath, encoding="utf-8")[:]
    print '1',df.columns,df[df.columns[0]].shape
    #########3
    df=df[df.columns[0]].values[:]#array
    segmented=[]
    for line in df[:]:#1153
        #print line
        ## complete name
        #line=complementDistrict(line,briefNameDic)#fail, use string_not_seg to get district,briefnameDistrict
        seg=cut_sentence(line)
        #print seg
        sz=[len(ch) for ch in seg.split(' ')];
        #print sz
        #seg_removeSingle=[ch for ch in seg.split(' ') if len(ch)>=2]# 7 days hotel is removed
        seg_removeSingle=seg.split(' ')#list

        if len(seg_removeSingle)>=1:
            newStr=' '.join(seg_removeSingle)
            #print newStr
            segmented.append(newStr)
        else:segmented.append(' ')

    print 'seg',len(segmented)

    ###
    pd.DataFrame({fname:segmented,fname+'_raw':df[:]}).\
        to_csv('../data/'+fname+'_segmented.csv',index=False,encoding='utf-8')



















