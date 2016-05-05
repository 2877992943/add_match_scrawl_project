#!/usr/bin/env python
# encoding=utf-8


import urllib
import urllib2
import json
import pandas as pd
import numpy as np



 


if __name__=="__main__":
	a=[1.,2.]
	ll=np.array([a,a,a,a,a]).reshape((-1,2))
	print ll
	####
	ll[1,:]=0.
	print ll
	########
	ll[np.where((ll==0.))]=np.nan
	print ll
	########
	df=pd.DataFrame(ll)
	print '1111',df,df.mean()
	df1=df.fillna(df.mean())
	
	#########
	 
	print df.values,df1.values

     




















