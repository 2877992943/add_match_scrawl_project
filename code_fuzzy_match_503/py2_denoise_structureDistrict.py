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
import chardet,re,jieba,time,requests




def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)



def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()



def getStructure(testStr,dataDic):
    testList=testStr.split(' ')
    #testList=[s.decode('utf-8') for s in testList]
    ##########
    structureList=[0]*2 #only use 2 level of ADDRESSstructurethe, 3rd district easy overlap
    #districtStr=0

    for level1,v1 in dataDic.items()[:]:
        name1=level1.strip(' ').decode('utf-8')
        if name1 in testList:# or name1[:-1] in testList[0] or name1[:-1] in testList[1]:
            #districtStr=name1
            structureList[0]=name1

        ###########3
        if isinstance(v1,dict):
            for level2,v2 in v1.items():
                name2=level2.strip(' ').decode('utf-8')
                if name2 in testList:
                    if structureList[0]==0:#incomplete address
                        structureList[1]=name2
                        structureList[0]=name1
                    else:
                        if structureList[0]==name1:
                            structureList[1]=name2


    ###############
    return structureList
if __name__=="__main__":
    start_time=time.time()

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]



    ##########
    #
    df=pd.read_csv('../data/'+fname+'_segmentDenoise_deep.csv',encoding='utf-8')

    #######segment,raw
    col=df.columns;print col #seg raw
    segSerial=df[fname+'_seg'].values[:];print 'segSerial shape',segSerial.shape
    rawSerial=df[fname+'_raw'].values
    deepSegSerial=df[fname+'_deepSeg'].values


    ############3
    #
    dataDic=grab('/home/yr/intellicredit/data/district_dict')
    totStructureDic={} # {seg_string:[beijing,haidian],...}

    for i in range(deepSegSerial[:].shape[0]):
        string=segSerial[i]
        string_deep=deepSegSerial[i]
        #print '?',isinstance(string,unicode),isinstance(string,str) #true false
        if isinstance(string,unicode):
            totStructureDic[string]=getStructure(string_deep,dataDic)

        if i%10000==0:print i

    #################
    # save
    store(totStructureDic,'../data/'+fname+'_DistrictDict_deep') #{segString:[beijing,haidian],... }not deep seg string
    pd.DataFrame({fname:totStructureDic.keys(),'district':totStructureDic.values()}).\
        to_csv('../data/'+fname+'_districtStructureShow.csv',index=False,encoding='utf-8')

    end_time=time.time()
    print 'time: %f minute'%((end_time-start_time)/float(60))














