#!/usr/bin/env python
# encoding=utf-8


import urllib
import urllib2
import json
import pandas as pd











def http_post(k,v):

    url_post='http://115.28.185.146:9080/ruleEngine/link'



    postdata={
    "obj_type" : "app",
    "obj_id" : "11111",
    "return_types" : [ "app", "blacklist", "blackquerylog" ],
    "tenant_id" : 0,
    #"pid" : "e7022dbb9670dccc756cec8feb32ee71d95af3d851c8c5f3f3b718b85e089dfe",
    "return_count" : 1000,
    "threshold" : 75
    }
    #update
    postdata[k]=v


    ###########
    #method 1
    #############3
    #url



    postdata1=urllib.urlencode(postdata)
    postdataj=json.dumps(postdata)
    header={'Content-Type': 'application/json'}
    req=urllib2.Request(url_post,postdataj,header)
    print 'request',(type(req))

    response=urllib2.urlopen(req)
    ############
    #read()  json.load() pd.read_json()
    #############3
    print 'response',type(response)
    response1=json.load(response);print '1',type(response1),response1#dict
    #response2=response.read();print '2',type(response2),response2 #str
    #response3=pd.read_json(response);print '3',response3 #not json
    #response3.to_csv()
    ########

    return response1



def analysis(response1,att0):
    #####initial dataFrame
    dataFrameDic={}
    for att in ['id','name','pid','mobile','time','home_address','home_phone',\
                    'work_name','work_address','work_phone']:
        dataFrameDic[att]=[]
    ####################


    name_pid_pair=[]
    #for dic in response1['pid']:
    for dic in response1[att0]:
        ##each person
        print '...'
        ####remove if no name no pid,invalid data
        if 'pid' not in dic['obj'] or 'name' not in dic['obj']:continue
        ####remove if name_pid pair appeared before,same person
        name_pid=[dic['obj']['name'],dic['obj']['pid'] ]
        if name_pid in name_pid_pair:continue
        if name_pid not in name_pid_pair:name_pid_pair.append(name_pid)
        #############

        for att in ['id','name','pid','mobile','time','home_address','home_phone',\
                    'work_name','work_address','work_phone']:
            if att in dic['obj']:
                print att+':',dic['obj'][att]
                dataFrameDic[att].append(dic['obj'][att])
            else:dataFrameDic[att].append('')
    #############
    pd.DataFrame(dataFrameDic).to_csv('../dict.csv',encoding='utf-8')
    #####return [  [node1i,att_edge,node2i],[],[]...]
    return pd.DataFrame(dataFrameDic)










if __name__=="__main__":
    seed=0
    k="pid";v="e7022dbb9670dccc756cec8feb32ee71d95af3d851c8c5f3f3b718b85e089dfe"
    k="home_address";v="北京市丰台区"
    response1=http_post(k,v) #input k,v ->dict
    print len(response1)
    if len(response1)>=1:
        df=analysis(response1,k);














