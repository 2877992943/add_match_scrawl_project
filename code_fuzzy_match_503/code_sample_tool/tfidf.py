#!/usr/bin/env python
# encoding=utf-8

from sklearn.feature_extraction.text import TfidfVectorizer

 

if __name__=="__main__":
	
	vectorizer  = TfidfVectorizer(ngram_range=(1, 2),min_df=1)
	corpus = [
	'This is a the first document.',
	'This is the second second document.',
	'And the third one.',
	'Is this the first document?',
	'金台里 人民日报社 爱玛 客 餐厅']#??客? 

	rst=vectorizer.fit_transform(corpus)
	print vectorizer.get_feature_names()
	rst=rst.toarray()
	print rst
	 
     




















