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



def locatebyAddr(address, city=None):
    '''
    根据地址确定经纬度，城市为可选项
    '''
    mykey='A9f77664caa0b87520c3708a6750bbdb'

    items = {'output': 'json', 'ak': mykey, 'address': address}
    if city:
        items['city'] = city

    r = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items)
    dictResult = r.json()
    return dictResult['result']['location'] if not dictResult['status'] else None

def main():

    address="湖南省长沙市"#"西安市观象台" 百度大厦
    city=''#"西安市"
    result = locatebyAddr(address, city)
    print(result),result.values()

if __name__=="__main__":
    start_time=time.time()

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]



    ##########
    #
    df=pd.read_csv('../data/'+fname+'_segmentDenoise.csv',encoding='utf-8')

    #######segment,raw
    col=df.columns;print col #seg raw
    segSerial=df[col[0]].values[:];print 'segSerial shape',segSerial.shape #[n,]
    rawSerial=df[col[1]].values


    ############3
    # geo
    geoDictTot={};i=0
    for string in segSerial[:]:

        #print '?',isinstance(string,unicode),isinstance(string,str) #true false
        if isinstance(string,unicode):
            address=string.replace(' ','').strip(' ')
            #print address
            result = locatebyAddr(address,'')
            #print address,result
            if isinstance(result,dict):
                geoList=result.values()#[28.213478230853, 112.97935278765]
            else:geoList=[0,0]
        if isinstance(string,unicode)==False:geoList=[0,0]
        geoDictTot[string]=geoList
        ############
        i+=1
        if i%100==0:print i//100


    #main()
    #################
    # save
    store(geoDictTot,'../data/'+fname+'_geoDict')
    pd.DataFrame({fname:geoDictTot.keys(),'geo':geoDictTot.values()}).\
        to_csv('../data/'+fname+'_geoShow.csv',index=False,encoding='utf-8')















    end_time=time.time()
    print 'time: %f minute'%((end_time-start_time)/float(60))

	#200 record take 1 minute, 50w would take 2500 minute












