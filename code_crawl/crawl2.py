#!/usr/bin/env python3
# encoding=utf-8









from urllib.request import urlopen

from bs4 import BeautifulSoup

import datetime
import random
import re,os


link0="http://www.pythonscraping.com/pages/page1.html"
link1="http://www.tripmh.com/cityroad.html"
link0="http://www.pythonscraping.com/pages/warandpeace.html"


"""
html=urlopen(link0)
bsObj=BeautifulSoup(html.read())
print (bsObj)
"""


def getTitle(url):
	try:
		html=urlopen(url)
	except HTTPError as e:
		return None
	
	try:
		bsObj=BeautifulSoup(html.read())
		title=bsObj.body.h1
		print ('.....',bsObj)
	except AttributerError as e:
		return None
	return title,bsObj

def static_url():
	title,bsObj=getTitle(link0)
	if title==None:
		print ('no title')
	else:print (title)
	########
	print ('find name green')
	nameList=bsObj.findAll('span',{'class':'green'})
	for name in nameList:
		print (name.get_text())


def getLinks1(articleUrl):
	link2='http://en.wikipedia.org/'+articleUrl
	html=urlopen(link2)
	bsObj=BeautifulSoup(html)
	return bsObj.find('div',{'id':'bodyContent'}).findAll('a',href=re.compile("^(/wiki/)((?!:).)*$"))
	"""
	for link in bsObj.findAll('a'):
		if 'href' in link.attrs:
			print (link.attrs['href'])"""
def scrapy1():
	random.seed(datetime.datetime.now())
	links=getLinks('/wiki/Kevin_Bacon');

	###
	for l in links:
		print (l)
	#####

	# further link
	i=1
	while len(links)>0 and i<=1:
		i+=1
		newArticle=links[random.randint(0,len(links)-1)].attrs['href']
		print ('new article',i,newArticle)
		links=getLinks(newArticle)

########################################3
def getLinks2(pageUrl):
	global pages
	pages=set()
	link2='http://en.wikipedia.org/'+pageUrl
	html=urlopen(link2)
	bsObj=BeautifulSoup(html)
	try:
		print (bsObj.h1.get_text())
		print (bsObj.find(id='mw-content-text').findAll('p')[0])
		print (bsObj.find(id='ca-edit').find('span').find('a').attrs['href'])
	except AttributeError:
		print ('some att absent in this page')

	############3
	for link in bsObj.findAll('a',href=re.compile('^(/wiki/)')):
		if 'href' in link.attrs:
			if link.attrs['href'] not in pages:
				newPage=link.attrs['href']
				print ('..............\n'+newPage)
				pages.add(newPage)
				getLinks2(newPage)
##########################################

def getRoad(add):
	#url='http://www.tripmh.com/road-list-37.html'
	url='http://www.tripmh.com/'+add
	html=urlopen(url)
	bsObj=BeautifulSoup(html)
	try:
		#print (bsObj.h1.get_text())
		#ll=bsObj.find('div',{'class':'cityroad'}).findAll('a',href=re.compile("(road-hotel-)"))
		ll=bsObj.findAll('a',href=re.compile("(road-hotel-)"))
		#print (ll)
		#print (bsObj.find(div='mw-content-text').findAll('p')[0])
		#print (bsObj.find(id='ca-edit').find('span').find('a').attrs['href'])
	except AttributeError:
		print ('some att absent in this page')

	#############3
	"""
	print ('num of road',len(ll))#485
	for elem in ll:
		print (elem.string)
	"""
	return [elem.string for elem in ll]


def getAllLinks():
	url='http://www.tripmh.com/cityroad.html'
	html=urlopen(url)
	bsObj=BeautifulSoup(html)

	try:

		ll=bsObj.findAll('a',href=re.compile("(road-list-)"))

	except AttributeError:
		print ('some att absent in this page')
	############
	totLink=[];totLinkStr=[]
	for link in ll:
		if link.attrs['href'] is not None:
			if link.attrs['href'] not in totLink:
				totLink.append(link.attrs['href'])
				totLinkStr.append(link.string)
	######
	"""
	print (len(totLink))
	for link in list(totLink)[:1]:
		print ('http://www.tripmh.com/'+link)
	"""
	return totLink,totLinkStr #['road-list-37.html',...]



if __name__=='__main__':
	"""
	#ll=getRoad()
	###########
	# get all links
	linkList,linkStringList=getAllLinks()# each link -> roads
	outPutfile=open('../data_crawl/names.txt','w')
	for elem in linkStringList:
		elem=elem.replace('名查询','')
		print (elem)
		outPutfile.write(str(elem));
		outPutfile.write('\n')
	outPutfile.close()

	#######
	# each link ,get roads
	allRoad=[];i=0
	for link in linkList[:]:
		roadList=getRoad(link)
		#allRoad=allRoad+roadList
		###########
		outPutfile=open('../data_crawl/roads_'+str(i)+'.txt','w')
		for elem in roadList:
			#print (elem)
			outPutfile.write(str(elem));
			outPutfile.write('\n')
		outPutfile.close()
		######
		i+=1;print (i,'success')
	"""

	#########
	# combine all txt
	inpath='../data_crawl/'
	roadList=[]
	for filename in os.listdir(inpath)[:]:
		content=open(inpath+'/'+filename,'r').read().strip('\n')
		contentList=content.split('\n')
		#print (contentList,len(content)) #['昆嵛路', '香山路', '张家产镇']
		roadList.extend(contentList)
	########
	print (len(roadList))
	#########
	outPutfile=open('../data_crawl/finalRoads.txt','w')
	for elem in roadList:
		#print (elem)
		if elem!=None:
			outPutfile.write(str(elem));
			outPutfile.write('\n')
	outPutfile.close()

























