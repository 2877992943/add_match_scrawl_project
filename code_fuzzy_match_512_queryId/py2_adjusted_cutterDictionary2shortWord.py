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
import chardet,re,jieba,time

def build_index_1gram(segSerial):#'klf jkld jkl'
    #############
    # get unique word,build index
    word_dic={};
    #for string in segSerial[:1000]:#each doc
    for ind in range(len(segSerial[:])):
        string=segSerial[ind]

        if type(string)==unicode:#some float
            strList=string.split(' ');
            for word in strList:# non digit ,length>1
                if word.isdigit()==False and len(word)>1:
                    if word not in word_dic:
                        word_dic[word]=[ind]
                    else:word_dic[word].append(ind)
    #####
    return word_dic


def build_index_2gram(segSerial):
    ###################################
    def is2Numbers(word2):
        d=[0 if w.isdigit() else 1 for w in word2 ]
        if d==[0,0]:return True
        else: return False
    def hasSingle(word2):
        sz=[len(w) for w in word2]
        if 1 in sz:return True
        else:return False
    ###########################################
    word_dic={};
    #for string in segSerial[:1000]:#each doc
    for ind in range(len(segSerial[:])):
        string=segSerial[ind]
        #print 'raw',string
        if type(string)==unicode:#some float
            strList=string.split(' ');# 'klj klj ewr'->[...]
            #for word in strList:# non digit ,length>1
            for wInd in range(len(strList))[1:]:
                word2=(strList[wInd-1].strip(' '),strList[wInd].strip(' ') );#print word2
                ##### word2=[x,xx] not [xx,xx]  #no [123,093]
                if hasSingle(word2) and ''.join(word2).isdigit()==False:
                    word2str=''.join(word2)
                    if word2str not in word_dic:
                        word_dic[word2str]=[ind]
                    else:word_dic[word2str].append(ind)
    return word_dic


def grab(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)



def store(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()

def transform_pinyin(word_dic):#'寿宝庄'->'shoubaozhuang'

    def word2pinyin(word):
        from xpinyin import Pinyin
        p = Pinyin()
        #word='寿宝庄'
        if isinstance(word,unicode)==False:
            word=unicode(word,'utf-8')
        ping=p.get_pinyin(word,' ')
        #print ping #'shou bao zhuang'
        return ping.replace(' ','')
    ##############3
    word_dic_p={} #{pinyin:[hanzi,hanzi]...}
    for word,indList in word_dic.items()[:10000]:
        #print word
        wordPINYIN=word2pinyin(word)
        if wordPINYIN not in word_dic_p:
            word_dic_p[wordPINYIN]=[word]
        else:

            word_dic_p[wordPINYIN].append(word)
    return word_dic_p





if __name__=="__main__":
    start_time=time.time()

    nameList=['homeAdd','workAdd','workname']
    fname=nameList[0]



    ##########
    # load index1gram
    word_dict=grab('../data/'+fname+'_wordIndexDict1')
    wordList=word_dict.keys();print 'len index',len(wordList)
    longWord345List=[]
    for word in wordList[:]:
        #print len(word),word
        if len(word)>=3:longWord345List.append(word)



    #### 1-gram --no single char

    #store(word_dic,'../data/'+fname+'_wordIndexDict1')
    pd.DataFrame({'word':longWord345List}).\
        to_csv('../data/'+fname+'_wordToBecut.csv',index=False,encoding='utf-8')






    end_time=time.time()
    print 'time: %f minute'%((end_time-start_time)/float(60))













