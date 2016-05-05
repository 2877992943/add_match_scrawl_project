#!/usr/bin/env python3
# encoding=utf-8

import sys;
#reload(sys);
#sys.setdefaultencoding('utf-8')

 


 



if __name__=="__main__":
	#addressFile='../data/blacklog_add_home.csv'
	#addressFile='../data/blacklog_workname.csv'
	addressFile='../data/blacklog_add_work.csv'
	
	content=open(addressFile,'rb').readlines()
	tot=[];error=0; 
	for line in content[:]:
		try:
			codeForm='GB18030'
			lineDecode=line.decode(codeForm)
			tot.append(lineDecode)
			print ('original code',codeForm,lineDecode)
		except:error+=1
	print ('zhongwen',len(tot),'fail decode',error)

    ##########to txt
	outfile1='../data/py3doc_workAdd.txt'
	outPutfile=open(outfile1,'w')
	for elem in tot:
		outPutfile.write('u'+elem);
		outPutfile.write('\n')
	outPutfile.close()



