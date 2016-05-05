#!/usr/bin/env python
# encoding=utf-8

import pandas as pd


def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)

def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()


def get_DistrictName():
    districtNameComplete=[]
    dataDic=grab('/home/yr/intellicredit/data/district_dict')
    for level1,v1 in dataDic.items()[:]:
        name=level1.strip(' ').decode('utf-8')
        districtNameComplete.append(name)
	####
        if isinstance(v1,dict):
            for level2,v2 in v1.items():
                name=level2.strip(' ').decode('utf-8')
                districtNameComplete.append(name)
                #######
                if isinstance(v2,dict):
                    for level3,v3 in v2.items():
                        name=level3.strip(' ').decode('utf-8')
                        districtNameComplete.append(name)


    return districtNameComplete




if __name__=='__main__':

	doc=get_DistrictName() #list
	print len(doc)
	
	store(doc,'/home/yr/intellicredit/data/'+'districtNameList0503')

	pd.DataFrame({'doc':doc}).\
        to_csv('/home/yr/intellicredit/data/'+'districtNameShow.csv',index=False,encoding='utf-8')







