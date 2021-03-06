#!/usr/bin/env python
# encoding=utf-8


"""
total db 50w
index->5w by all string-level word
1st filter conflict district: 'beijing' 'no-beijing' ,district-level,feature->vector 
2 tfidf :string-level weight
3 geo: latitude longitude to kilometer 


"""

#import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

import pandas as pd
import chardet,re,jieba,time,math,random,copy,requests
import numpy as np

def get_DistrictName():
    districtNameComplete=[]
    dataDic=grab('/home/yr/intellicredit/data/district_dict')
    for level1,v1 in dataDic.items()[:]:
        name=level1.strip(' ').decode('utf-8')
        districtNameComplete.append(name)
        if isinstance(v1,dict):
            for level2,v2 in v1.items():
                name=level2.strip(' ').decode('utf-8')
                districtNameComplete.append(name)


    return districtNameComplete


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

def calc_EuDistance(test,compare):#[1,d],[n,d]
    testMat=np.tile(test,(compare.shape[0],1));#[1,d]->[n,d]
    dist=testMat-compare
    dist=np.sqrt(np.sum(dist*dist,axis=1))#[n,d]->[n,]
    return dist

def strUnique(string):
    strList=string.split(' ')
    uniqueList=[]
    for w in strList:
        if w not in uniqueList:
            uniqueList.append(w)
    return ' '.join(uniqueList)

def score(testStr,candList1):
    batch_sz=1000
    from sklearn.feature_extraction.text import TfidfVectorizer
    totCandidate=[];totInd=[]
    batch_num=int(math.ceil(len(candList)/float(batch_sz))) #51/50.0->2.0
    for batch in range(batch_num)[:]:
        corpus=np.array(candList1)[batch*batch_sz:(batch+1)*batch_sz];#list print corpus[0],corpus[1] #'北京市 海淀区 西三旗' '人民日报社 爱玛 客 餐厅'
        #############
        # tf idf
        vectorizer = TfidfVectorizer(ngram_range=(1,1),min_df=1)
        corpus=list(corpus)
        corpus.append(testStr)
        rst=vectorizer.fit_transform(corpus)#the last one is testStr
        #print vectorizer.get_feature_names()
        #for w in vectorizer.get_feature_names():
            # print w ##no '客'
        rst=rst.toarray()
        #print 'feature',rst.shape #[n,dim]
        ################
        # calculate distance
        test=rst[-1,:].reshape((1,-1))#[1,d]
        compare=rst[:-1,:] #[n,d]
        dist=calc_EuDistance(test,compare);#print 'eu-dist min max',np.min(dist),np.max(dist)
        rank=np.argsort(dist)[:50]#index ,from smallScore->largeScore sort
        candidateList=[corpus[ii] for ii in rank]#list
        totCandidate=totCandidate+candidateList
        #
        indList=[batch*batch_sz+ij for ij in rank]
        totInd=totInd+indList
        #score=dist[rank] #array
        #for i in range(len(candidateList))[:]:
         #   print candidateList[i],'eu-dist',score[i]
    #############
    print 'tot candidate',len(totCandidate)
    ###################
    # total candidate
    ## idf
    vectorizer = TfidfVectorizer(ngram_range=(1,1),min_df=1)
    corpus=totCandidate
    corpus.append(testStr)
    rst=vectorizer.fit_transform(corpus)
    rst=rst.toarray()
    # distance
    test=rst[-1,:].reshape((1,-1))#[1,d]
    compare=rst[:-1,:] #[n,d]
    dist=calc_EuDistance(test,compare)
    # pick up distance<=1.2
    distInd=np.where(dist<=1.2)[0]#row index
    dist=dist[distInd]
    corpus=[corpus[ij] for ij in distInd]
    totIndArr=np.array(totInd)[distInd]
    #
    rank=np.argsort(dist)#[:20]#index ,from smallScore->largeScore sort
    candidateList=[corpus[ii] for ii in rank]#list
    score=dist[rank] #array
    for i in range(len(candidateList))[:]:
        print strUnique(candidateList[i]),'eu-dist',score[i]
    ############
    return totIndArr





def score_str_geo(testStr1,candList1,locArr,testArr):
    ############################
    from sklearn.feature_extraction.text import TfidfVectorizer
    # tf idf
    vectorizer = TfidfVectorizer(ngram_range=(1,1),min_df=1)
    corpus=candList1
    corpus.append(testStr1);
    strArr=vectorizer.fit_transform(corpus)#the last one is testStr
    strArr=strArr.toarray(); #[n,d] tfidf word weight matrix
    ################
    # calculate distance
    #
    jingweiduArr=np.concatenate((locArr.reshape((-1,2)),testArr.reshape((1,2)) ),axis=0); #[n,2]
    jingweiduArr=fill0withMean(jingweiduArr);#print jingweiduArr#[n,2]
    #jingweiduArr=normalize(jingweiduArr)
    #geoDistance=getGeoDistance(testArr.reshape((1,2)),locArr.reshape((-1,2)) ) #[n,]
    #print '?',strArr.shape,jingweiduArr.shape,geoDistance.reshape((-1,1)).shape,geoDistance#[n,d][n,2],[n-1,1]
    rst=np.concatenate((strArr,jingweiduArr),axis=1);print 'final', rst.shape #[n,d]
    #
    test=rst[-1,:].reshape((1,-1))#[1,d]
    compare=rst[:-1,:] #[n,d]
    #compare=np.concatenate((compare,geoDistance.reshape((-1,1)) ),axis=1)
    dist=calc_EuDistance(test,compare);#print 'eu-dist min max',np.min(dist),np.max(dist)
    # pick up distance<=1.2
    #distInd=np.where(dist<=1.2)[0]#row index
    #dist=dist[distInd]
    #corpus=[corpus[ij] for ij in distInd]
    #
    ranks=np.argsort(dist)#[:20]#index ,from smallScore->largeScore sort
    return ranks,dist

def fill0withMean(jingweiduArr):
    jingweiduArr[np.where((jingweiduArr==0.))]=np.nan
    df=pd.DataFrame(jingweiduArr)
    df.fillna(df.mean())
    arr=df.values
    return arr

def normalize(jingweiduArr):#[n,2]
    n,d=jingweiduArr.shape
    minx=np.min(jingweiduArr,axis=0).reshape((1,-1)) #[1,2]
    maxx=np.max(jingweiduArr,axis=0).reshape((1,-1))
    gap=np.tile(maxx-minx,(n,1))#[1,2]->[n,2]
    mat=jingweiduArr-np.tile(minx,(n,1)) #[1,2]->[n,2]
    mat=mat/gap
    return mat


def latlng2distance(Lat_A, Lng_A, Lat_B, Lng_B):#32 118
    from math import *

    ra = 6378.140  # 赤道半径 (km)
    rb = 6356.755  # 极半径 (km)
    flatten = (ra - rb) / ra  # 地球扁率
    rad_lat_A = radians(Lat_A)
    rad_lng_A = radians(Lng_A)
    rad_lat_B = radians(Lat_B)
    rad_lng_B = radians(Lng_B)
    pA = atan(rb / ra * tan(rad_lat_A))
    pB = atan(rb / ra * tan(rad_lat_B))
    xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
    c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
    c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (xx + dr)
    return distance
def getGeoDistance(test,candidate): #[1,2],[n,2]
    eps=0.0001
    #print test,candidate
    dist=[latlng2distance(test[0,0]+eps,test[0,1]+eps,ll[0],ll[1]) for ll in candidate]
    return np.array(dist)



def get2gram(strList):#list ['北京市', '区', '西三旗']
    def hasSingle(word2):
        sz=[len(w) for w in word2]
        if 1 in sz:return True
        else:return False
    #####################
    gram2List=[]
    for wInd in range(len(strList))[1:]:
        #w=strList[wInd]
        #if isinstance(w,unicode)==False:w=unicode(w)
        word2=(strList[wInd-1].strip(' '),strList[wInd].strip(' ') );#print word2
        ##### word2=[x,xx] not [xx,xx]  #no [123,093]
        if hasSingle(word2) and ''.join(word2).isdigit()==False:
            word2str=''.join(word2);#print word2str
            gram2List.append(word2str)
    ##############
    return gram2List #['北京市区', '区西三旗']

def addSingle2Bigram(candiArr,testStr):
    #print 'add single'
    # test
    testList1=testStr.split(' ')
    testList2=get2gram(testList1)
    testStr=' '.join(testList2+testList1);#print testStr
    ######### candidate
    canList=[]
    for i in range(len(candiArr))[:]:
        strList1=candiArr[i].split(' ');#print strList1
        strList2=get2gram(strList1);#print strList2
        stringi=' '.join(strList2+strList1);#print stringi
        canList.append(stringi)
    return canList,testStr


def reduceDistrictWeight(candList,testStr):
    print 'reduce district weight...'
    districtNameCompleteList=get_DistrictName()#33 district name
    ###test string
    testStrList1=copy.copy(testStr.split(' '))
    for word in testStr.split(' '):
        if word not in districtNameCompleteList:
            testStrList1.append(word)
    testStr=' '.join(testStrList1);#print testStr
    ###########candidate
    candList1=[]
    for cand in candList:
        obsList=copy.copy(cand.split(' '))
        for word in cand.split(' '):
            if word not in districtNameCompleteList:
                obsList.append(word)
        candList1.append(' '.join(obsList))
    #print candList1[0]
    return candList1,testStr


def filter_conflict_district(testDistrictList,candiArr,structureDistrictDic):#['beijing','haidian']
    candiListFiltered=[]
    for candStr in candiArr[:]:
        cand_districtList=structureDistrictDic[candStr]#[beijing,haidian]
        #print candStr,'|',cand_districtList[0],cand_districtList[1]
        if cand_districtList[0] in [testDistrictList[0],0]:
            if cand_districtList[1] in [testDistrictList[1],0]:
                candiListFiltered.append(candStr);#print 'pass...'
    return candiListFiltered


def locatebyAddr(address, city=None):
    """string address ->[jing wei]"""
    mykey='A9f77664caa0b87520c3708a6750bbdb'

    items = {'output': 'json', 'ak': mykey, 'address': address}
    if city:
        items['city'] = city

    r = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items)
    dictResult = r.json()
    return dictResult['result']['location'] if not dictResult['status'] else None



if __name__=="__main__":
    start_time=time.time()

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]



    print 'index...'
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
    rng=355126#random.choice(range(string_seg.shape[0])) #6
    query=string[rng];print 'query',rng
    query_preprocess=string_seg[rng];print query_preprocess
    query_preprocess=query_preprocess.split(' ')#list
    #print query_preprocess
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
    print '2gram...'
    query_preprocess2=get2gram(query_preprocess)#['a','erf']->['aerf']
    print query_preprocess2

    docInd2=[]
    for word in query_preprocess2:
        #print word
        if word in wordIndDic2:
            indList2=wordIndDic2[word];
            docInd2=docInd2+indList2
    print 'docind2',len(docInd2),len(set(docInd2))


    print 'remove conflict district12'
    ##############
    # remove conflict district beijing-hebei, chaoyang-haidian
    structureDistrictDic=grab('../data/'+fname+'_DistrictDict')#{segString:[beijing,haidian],..}
    #
    candiInd=list(set(docInd1+docInd2))
    candiArr=string_seg[candiInd][:];print 'candidate',candiArr.shape #[n,]
    ##test
    testStr=string_seg[rng];print 'test',testStr
    testDistrictList=structureDistrictDic[testStr];print testDistrictList[0],testDistrictList[1]
    ##candidate
    candList=filter_conflict_district(testDistrictList,candiArr,structureDistrictDic) #segString
    print 'candidate',len(candList)




    print 'string level,tfidf...'
    ###################
    # pair score :string-level-tfidf,geo-level
    candiArr=np.array(candList); #no bigram in string
    #testStr=string_seg[rng];print testStr #segString
    #[爱玛, 客, 餐厅] ->[爱玛客 ,客餐厅]
    candList1,testStr1=addSingle2Bigram(candiArr,testStr);#print '111',testStr
    candList1,testStr1=reduceDistrictWeight(candList1,testStr1)
    candIndArr=score(testStr1,candList1)

    #for ind in candIndArr:
     #   print '?',candiArr[ind]
    ##### after tfidf(string level), geo(location)

    print 'geo level...'
    #candidate
    totLocList=[]
    for ind in candIndArr:
        loc0=[0.,0.]#must be float, not int
        #print candiArr[ind]
        candStr_noSeg=candiArr[ind].replace(' ','')#'深圳市 宝安区'->'深圳市宝安区'
        loc=locatebyAddr(candStr_noSeg)
        if isinstance(loc,dict):loc0=loc.values()
        totLocList.append(loc0)
        print candStr_noSeg,loc0
    #test
    testLoc=locatebyAddr(testStr.replace(' ',''))
    testLoc=[testLoc.values() if isinstance(testLoc,dict) else [0.,0.]][0];print testStr,testLoc
    #######


    candiArr=candiArr[candIndArr]; #[10003,54234,90,2]same ind for distance,stringAdd
    candList1,testStr1=addSingle2Bigram(candiArr,testStr);
    candList1,testStr1=reduceDistrictWeight(candList1,testStr1);
    ranks,dist=score_str_geo(testStr1,candList1,np.array(totLocList),np.array(testLoc))
    for r in ranks:
        print candiArr[r],dist[r]




    ########
    end_time=time.time()
    print 'time: %f minute'%((end_time-start_time)/float(60))













