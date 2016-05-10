#!/usr/bin/env python
# encoding=utf-8


"""
total db 50w
index->5w by all string-level word
1st filter: 'beijing' 'no-beijing' ,district-level,feature->vector 
2 tfidf :string-level weight
3 geo use jingweidu directly, no kilometer

4 totalDistance=(1-theta)*dist_string+theta*dist_geo [all 0-1]


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

def normalize(jingweiduArr):#[n,2]
    n,d=jingweiduArr.shape
    minx=np.min(jingweiduArr,axis=0).reshape((1,-1)) #[1,2]
    maxx=np.max(jingweiduArr,axis=0).reshape((1,-1))
    gap=np.tile(maxx-minx,(n,1))#[1,2]->[n,2]
    mat=jingweiduArr-np.tile(minx,(n,1)) #[1,2]->[n,2]
    mat=mat/gap
    return mat

def score(testStr,candList1):#deepSeg
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
        mid_dist=np.min(dist)+(np.max(dist)-np.min(dist) )/4.*3.
        ##2 kinds of candidate select strategy
        rank=np.where(dist<=mid_dist)[0];#print 'mid dist',rank.shape
        if rank.shape[0]<50:
            rank=np.argsort(dist)[:50]#index ,from smallScore->largeScore sort
        ## string in list
        candidateList=[corpus[ii] for ii in rank]#list
        totCandidate=totCandidate+candidateList
        # ind in list
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
    corpus=totCandidate #after batches of candidate
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
    return totIndArr,dist




def fill0withMean(jingweiduArr):
    #print jingweiduArr
    jingweiduArr[np.where((jingweiduArr==0.))]=np.nan
    df=pd.DataFrame(jingweiduArr);
    df1=df.fillna(df.mean())
    arr=df1.values
    return arr


def kilometerClose(locArr,testArr): #[n,2] [1,2]
    ################
    # calculate geo distance
    rst1=np.concatenate((locArr.reshape((-1,2)),testArr.reshape((1,2)) ),axis=0);
    rst1=fill0withMean(rst1);print 'fill0 with mean',rst1
    test=rst1[-1,:].reshape((1,-1))#[1,d]
    compare=rst1[:-1,:] #[n,d]
    distArr=getGeoDistance(test,compare)# [1,2],[n,2]->[n,]
    print 'geo->km',distArr
    #indClose=np.where(distArr<=1)[0]
    return distArr

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


def filter_conflict_district(testDistrictList,candiArr,candiArr_deep,structureDistrictDic):#['beijing','haidian']
    candiListFiltered=[];candiListFiltered_deep=[]
    ij=0
    for candStr in candiArr[:]:
        cand_districtList=structureDistrictDic[candStr]#[beijing,haidian]
        #print candStr,'|',cand_districtList[0],cand_districtList[1]
        if cand_districtList[0] in [testDistrictList[0],0]:
            if cand_districtList[1] in [testDistrictList[1],0]:
                candiListFiltered_deep.append(candiArr_deep[ij]);#print 'pass...'
                candiListFiltered.append(candStr)
        ij+=1
    return candiListFiltered,candiListFiltered_deep


def locatebyAddr(address, city=None):
    """string address ->[jing wei]"""
    mykey='A9f77664caa0b87520c3708a6750bbdb'

    items = {'output': 'json', 'ak': mykey, 'address': address}
    if city:
        items['city'] = city
    try:
        r = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items)
    except:
        time.sleep(3)
        r = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items)
    dictResult = r.json()
    return dictResult['result']['location'] if not dictResult['status'] else None



def getKiloMeter(testStr,candInd,candiArr): #seg_str
    noGeoDist=10000
    totGeoInfoList=[]
    testLoc=locatebyAddr(testStr.replace(' ',''))#seg_string->noSeg_string
    #testLoc=[testLoc.values() if isinstance(testLoc,dict) else [0,0]][0];#print testLoc
    if isinstance(testLoc,dict)==False:
        testLoc=[0,0]
        print 'no loc for test address'
        #totGeoInfoList.append('test no geo')
        totGeoInfoList=[ [candiArr[cind],noGeoDist] for cind in candInd]
    else:#test address location exist
        testLoc=testLoc.values()
        candDistList=[]
        for ind in candInd:#after tfidf ind ,each candidate
            locCand=[0,0]
            #print candiArr[ind]
            candStr_noSeg=candiArr[ind].replace(' ','')#'深圳市 宝安区'->'深圳市宝安区'
            loc=locatebyAddr(candStr_noSeg)
            if isinstance(loc,dict): #candidate str location exist
                locCand=loc.values()
                #print testLoc,np.array(testLoc),loc0,np.array(loc0)
                dist=getGeoDistance(np.array(testLoc).reshape((1,2)),np.array(locCand).reshape((1,2)) )
                #####
                #print candStr_noSeg,locCand,dist[0]
                candDistList.append([candiArr[ind],dist[0]])#[ [segStr,km],[]...]
            else:candDistList.append([candiArr[ind],noGeoDist])
        totGeoInfoList=candDistList
    ##############sort
    tmpDict=dict(candDistList)
    sortll=sorted(tmpDict.iteritems(),key=lambda asd:asd[1],reverse=False)#[ [noSegStr,num],,[]...]
    for elem in sortll:
        print elem[0],elem[1]
    return totGeoInfoList


def removeDoorNumber(testStr,candInd,candiArr):
    print 'remove door num', testStr
    candStrList=[]
    for ind in candInd:
        candL=candiArr[ind].split(' ')
        print candL
        if len(candL)>=3 and candL[-1].isdigit():del candL[-1]
        if len(candL)>=4 and candL[-2].isdigit():del candL[-2]
        ####
        candStrList.append(' '.join(candL) )
    #######
    testL=testStr.split(' ')
    if len(testL)>=3 and testL[-1].isdigit():del testL[-1]
    if len(testL)>=4 and testL[-2].isdigit():del testL[-2]
    testStr=' '.join(testL)
    return testStr,candStrList

def score_editDist(testStr,candList):#segDeepstr  :count how many words are hit
    print 'edit dist'
    simCandList=[]
    testL=testStr.split(' ')
    for cand in candList:
        #print cand
        candL=cand.split(' ')#str->list
        editScore1=sum([1 for s in candL if s in testL])/float(len(candL))
        editScore2=sum([1 for s in testL if s in candL])/float(len(testL))
        if len(candL)>len(testL):lenScore=len(testL)/float(len(candL))
        else:lenScore=len(candL)/float(len(testL))
        #print editScore1,editScore2,lenScore,len(candL),len(testL)#,testL,candL
        ########
        simCandList.append([cand,1./(editScore1*editScore2*lenScore) ]) #[segDeepStr,score]


    return simCandList



if __name__=="__main__":
    start_time=time.time()

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]



    print 'index...'
    ##########
    # load index ,load database ,load query
    db_df=pd.read_csv('../data/'+fname+'_segmentDenoise_deep.csv',encoding='utf-8')
    print db_df.columns #homeAdd', u'homeAdd_raw'
    wordIndDic1=grab('../data/'+fname+'_wordIndexDict1_deep')
    #wordIndDic2=grab('../data/'+fname+'_wordIndexDict2')


    ############
    # query
    string=db_df[fname+'_raw'].values;print string.shape
    string_seg=db_df[fname+'_seg'].values         #for geo search
    string_deepSeg=db_df[fname+'_deepSeg'].values #for index search
    rngList=random.sample( range(string_deepSeg.shape[0]),10)#472535#355126#random.choice(range(string_seg.shape[0])) #6
    testDict_km={};testDict_tfidf={}#;within1kmTestDict={};strEditSimDict={};
    testDict_str={}
    for rng in rngList:
        #rng=336812#115386#142636#451663 18632
        query=string[rng];print 'query no seg str',rng
        query_preprocess_deep=string_deepSeg[rng];print 'str seg deep',query_preprocess_deep
        query_preprocess=string_seg[rng]
        #ss='甘井子区 千 山路 义迎路 606'
        #print np.where((string_seg==ss.decode('utf-8') ))
        query_preprocess_deepList=query_preprocess_deep.split(' ')#list
        #print query_preprocess
        ###########
        # get doc-ind1

        docInd1=[]
        for word in query_preprocess_deepList:
            #print word
            if word in wordIndDic1:
                indList1=wordIndDic1[word];
                docInd1=docInd1+indList1
        print 'docind',len(docInd1),len(set(docInd1))


        """
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
        """

        print 'remove conflict district12'
        ##############
        # remove conflict district beijing-hebei, chaoyang-haidian
        structureDistrictDic=grab('../data/'+fname+'_DistrictDict_deep')#{segString:[beijing,haidian],..}not segDeepStr
        #
        #candiInd=list(set(docInd1+docInd2))
        candiInd=list(set(docInd1))
        candiArr_deep=string_deepSeg[candiInd][:]; print 'candidate',candiArr_deep.shape #[n,]
        candiArr=string_seg[candiInd]
        ##test district name
        testStr=query_preprocess;print 'test str seg',testStr #segStr not deepSeg
        testDistrictList=structureDistrictDic[testStr];print testDistrictList[0],testDistrictList[1]#beijing,haidian
        ##candidate
        candList,candDeepList=filter_conflict_district(testDistrictList,candiArr,candiArr_deep,structureDistrictDic) #segDeepString
        print 'candidate',len(candList)




        print 'string level,tfidf...'
        ###################
        # pair score :string-level-tfidf,geo-level
        candiArr=np.array(candList); #no bigram in string
        candiArr_deep=np.array(candDeepList)
        #testStr=string_seg[rng];print testStr #segString
        #[爱玛, 客, 餐厅] ->[爱玛客 ,客餐厅]
        #candList1,testStr1=addSingle2Bigram(candiArr,testStr);#print '111',testStr
        candList1,testStr1=reduceDistrictWeight(candDeepList,query_preprocess_deep)
        candInd,dist_tfidf=score(testStr1,candList1) #index of candiArr
        tfidfCloseList=[ [candiArr_deep[candInd[i]],dist_tfidf[i]] for i in range(len(candInd)) ]#first column [strDeepSeg,score]
        testDict_tfidf[query_preprocess]=tfidfCloseList
        ##### after tfidf(string level), geo(location)

        #######
        # geo ->kilometer within 1 km
        print 'geo level...'
        #
        totGeoInfoList=getKiloMeter(query_preprocess,candInd,candiArr) #str_seg, not deepSeg
        #
        testDict_km[query_preprocess]=totGeoInfoList #second columns[ [candidate],[candidate]...] [cand]=[string_Seg,kilometer]
        #print 'end',query_preprocess,string_seg[rng]
        #closeGeoCandiList=[cand for cand in totGeoInfoList if cand[1]<=1]
        #remoteCandiList=[cand for cand in totGeoInfoList if cand[1]>1]
        #within1kmTestDict[query_preprocess]=closeGeoCandiList# third columns in final form

        ########
        # string level partial match
        candScoreList=score_editDist(query_preprocess_deep,candiArr_deep[candInd])#deepSeg,->[ [segDeep,score],[]...]
        #strCloseList=[ [candiArr_deep[candInd[i]],dist_str[i]] for i in range(len(candInd)) ]#first column [strDeepSeg,score]
        testDict_str[query_preprocess]=candScoreList

        #strSimList=editDist(remoteCandiList,testStr)
        #closeStrList=[cand for cand in tfidfCloseList if cand[1]<=1]
        #[[candidate],[candidate]...] [cand]=[string_Seg,score]->[str_seg,..]
        #strEditSimDict[query_preprocess]=closeStrList





    ############3
    pd.DataFrame({'query':testDict_tfidf.keys(),'allCand_tfidf':testDict_tfidf.values(),'allCand_geo':testDict_km.values(),'editdist':testDict_str.values()}).\
        to_csv('../data/'+fname+'_returnQuery.csv',index=False,encoding='utf-8')
    ########
    end_time=time.time()
    print 'time: %f minute'%((end_time-start_time)/float(60))





"""
string level
福永区桥 桥南村 深圳市 福永区 桥 南村 eu-dist 0.0
蒋家桥 桥南村 蒋家 桥 南村 eu-dist 1.16611590677
虹桥镇桥 桥南村 乐清市 虹桥镇 桥 南村 eu-dist 1.18571642714
虹桥镇桥 桥南村 乐清市 虹桥镇 桥 南村 eu-dist 1.18571642714

geo level...
深圳市福永区桥南村 [22.677660583608, 113.83109606853]
蒋家桥南村 [31.625392385787, 120.74300443478]
乐清市虹桥镇桥南村 [28.234040715456, 121.06271226767]
乐清市虹桥镇桥南村 [28.234040715456, 121.06271226767]


geo [  0.          11.30647521   9.11973865   9.11973865] (4,)
string [ 0.          1.25755716  1.25593052  1.25593052] (4,)
normalize (0,1)
[[ 0.          0.        ]
 [ 1.          1.        ]
 [ 0.99870651  0.80659432]
 [ 0.99870651  0.80659432]]
combine by theta... (4,)
[ 0.          1.          0.90265041  0.90265041]

福永区桥 桥南村 深圳市 福永区 桥 南村 eu-dist combine string + geo 0.0
虹桥镇桥 桥南村 乐清市 虹桥镇 桥 南村 eu-dist combine string + geo 0.902650412896
虹桥镇桥 桥南村 乐清市 虹桥镇 桥 南村 eu-dist combine string + geo 0.902650412896
蒋家桥 桥南村 蒋家 桥 南村 eu-dist combine string + geo 1.0

geo distance is absolute, should not normalized
"""










