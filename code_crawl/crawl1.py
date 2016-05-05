#!/usr/bin/env python3
# encoding=utf-8









from urllib.request import urlopen

from bs4 import BeautifulSoup

import datetime
import random
import re


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

if __name__=='__main__':

	getLinks2('/wiki/Kevin_Bacon')





















