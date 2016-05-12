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
            sheng=dis.strip()
            dataDic[sheng]={}
        if level==2:
            shi=dis.strip()
            dataDic[sheng][shi]={}
        if level==3:
            qu=dis.strip()
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

    """
    ###########
    import pprint
    pp=pprint.PrettyPrinter(depth=6)
    pp.pprint(dataDic)"""


def get_geoInfo(addressName):
    import urllib
    import hashlib
    import requests


    ak='TjQqVP9gwVBe8eYFPEDVR5N4GhIeEWqH'#api
    sk='juv2nIscPd11fzIgm77sqRpjOeFYoOFF'#security


    #addressName='百度大厦'
    queryStr = '/geocoder/v2/?address='+addressName+'&output=json&ak='+ak
    #print queryStr
    encodedStr = urllib.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodedStr + sk
    snStr = hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()

    reqStr = 'http://api.map.baidu.com/geocoder/v2/?address='+addressName+'&output=json&ak='+ak+'&sn=' + snStr

    r = requests.get(reqStr)
    dictResult = r.json()
    #print dictResult['result']['location'] if not dictResult['status'] else None
    rst=dictResult['result']['location'] if not dictResult['status'] else None
    return rst


if __name__=="__main__":
    """
    #############
    # generate dict from csv for district,need to re generate ,strip

    path = "/home/yr/intellicredit/data/2014_district.csv"
    dataDic=generate_json(path);#print dataDic
    store(dataDic,'/home/yr/intellicredit/data/district_dict')
    print_dict(dataDic)
    #######
    """
    ###############
    # load dict

    dataDic=grab('/home/yr/intellicredit/data/district_dict')
    #print_dict(dataDic)
    ##############
    #get geo
    geoDic=dataDic.copy()
    #geo=get_geoInfo('百度大厦')
    for level1,v1 in dataDic.items()[:]:
        if isinstance(v1,dict) and len(v1)==0:
            address=level1.strip()
            geoDic[level1]=get_geoInfo(address)
            #print level1,geoDic[level1]
        else:
            for level2,v2 in v1.items()[:]:
                if isinstance(v2,dict) and len(v2)==0:
                    address=level1.strip()+level2.strip()
                    geoDic[level1][level2]=get_geoInfo(address)
                    #print level1+level2,geoDic[level1][level2]
                else:
                    for level3,v3 in v2.items()[:]:
                        if isinstance(v3,dict) and len(v3)==0:
                            address=level1.strip()+level2.strip()+level3.strip()#unicode(level1+level2+level3,encoding='utf-8')
                            geoDic[level1][level2][level3]=get_geoInfo(address)
                            #print address,geoDic[level1][level2][level3]

    store(geoDic,'/home/yr/intellicredit/data/district_dict_location')




















