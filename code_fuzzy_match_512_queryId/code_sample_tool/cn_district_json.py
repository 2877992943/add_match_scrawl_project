#!/usr/bin/env python
# encoding=utf-8


import urllib
import urllib2
import json
import pandas as pd











def generate_json(filename):
    dataDic={}
    df=pd.read_csv(filename)

    print df.columns
    for dis,level in zip(df['dis'][:].values,df['level'][:].values):
        #print dis.strip(),level
        ##########sheng1 shi2 qu3
        if level==1:
            sheng=dis
            dataDic[sheng]={}
        if level==2:
            shi=dis
            dataDic[sheng][shi]={}
        if level==3:
            qu=dis
            dataDic[sheng][shi][qu]={}


    return dataDic




def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()

def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)



def print_dict(dataDic):
    for k,v in dataDic.items():
        print k
        if isinstance(v,dict) and len(v)>0:
            for kk,vv in v.items():
                print kk
                if isinstance(vv,dict) and len(vv)>0:
                     for kkk,vvv in vv.items():
                         print kkk




if __name__=="__main__":
    path = "../data/2014_district.csv"
    dataDic=generate_json(path);print dataDic
    store(dataDic,'../data/district_dict')
    #print_dict(dataDic)
    #######
    dic=grab('../data/district_dict')
    print_dict(dic)














