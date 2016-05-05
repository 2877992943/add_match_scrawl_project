#!/usr/bin/env python
# encoding=utf-8


"""segment,do not remove single word, use forward/backward_pair to match, do  keep len=1 word in sentence
1)get district,city etc structure from address,
2)remove noise like ( ) |first repeated word |number |appear in the end, not begaining of addresss

denoise
index_1:1-gram,hanzi
"""

#import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re,jieba,time
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

def score_notwell(pair):#[string,string]
    from fuzzywuzzy import fuzz
    score1=fuzz.token_sort_ratio(pair[0],pair[1])
    score2=fuzz.partial_ratio(pair[0],pair[1])
    return (score1+score2)/2.
def score(pair):
    str1List=pair[0].split(' ')
    str2List=pair[1].split(' ')
    str1=pair[0].replace(' ','')
    str2=pair[1].replace(' ','')
    ############
    sc1=0
    for ch in str1List:
        if ch in str2:sc1+=1
    sc1/=float(len(str1List))
    ############
    sc2=0
    for ch in str2List:
        if ch in str1:sc2+=1
    sc2/=float(len(str2List))
    return (sc1+sc2)/2.






if __name__=="__main__":
    start_time=time.time()

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]



    ##########
    # load index ,load database ,load query
    db_df=pd.read_csv('../data/'+fname+'_segmentDenoise.csv',encoding='utf-8')
    print db_df.columns #homeAdd', u'homeAdd_raw'
    wordIndDic1=grab('../data/'+fname+'_wordIndexDict1')
    wordIndDic2=grab('../data/'+fname+'_wordIndexDict2')
    ############
    # query
    string=db_df['homeAdd_raw'].values;print string.shape
    string_seg=db_df['homeAdd'].values
    rng=10005
    query=string[rng]
    query_preprocess=string_seg[rng];
    query_preprocess=query_preprocess.split(' ')#list
    print 'query',query_preprocess
    ###########
    # get doc-ind1

    docInd1=[]
    for word in query_preprocess:
        #print word
        if word in wordIndDic1:
            indList1=wordIndDic1[word];
            docInd1=docInd1+indList1
    print 'docind',len(docInd1),len(set(docInd1))

    ################
    # get doc-ind2
    ###################3
    # score
    testStr=string_seg[rng]
    print 'test',testStr,string_seg[rng],score([testStr,string_seg[rng]])


    scoreList=[]
    for ind in docInd1[:]:
        strTBD=string_seg[ind]
        #print 'to be paired',strTBD
        #pair=[testStr.replace(' ',''),strTBD.replace(' ','')]
        pair=[testStr,strTBD]
        sc=score(pair);
        scoreList.append(sc)
    ###########rank score
    numCandidate=50
    indRank=np.argsort(np.array(scoreList))[::-1][:numCandidate];print indRank
    scoreRank=sorted(scoreList)[::-1][:numCandidate]
    candidate=np.array(docInd1)[indRank]
    for i in range(len(candidate)):
        can=candidate[i]
        print string_seg[can],scoreRank[i]










    end_time=time.time()
    print 'time: %f minute'%((end_time-start_time)/float(60))













