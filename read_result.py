# _*_ coding:utf-8 _*_
import json
import urllib
from bs4 import BeautifulSoup
import re
import lxml
from lxml.html.clean import Cleaner
import operator
import string
import urllib2
import requests
import collections
from selenium import webdriver
import wget
import os
#gives frequency
def word_count(string):
	my_string = string.lower().split()
	my_dict = {}
	for item in my_string:
		if item in my_dict:
			my_dict[item] += 1
		else:
			my_dict[item] = 1
	f1=open('stop.txt','r')
	stopFile=f1.read()
	for word in stopFile.split():
		if  word in my_dict:
			del my_dict[word]
	sorted_dict = collections.OrderedDict(sorted(my_dict.items(), key=operator.itemgetter(1)))
	return sorted_dict
#gives minimum position from word
def minDist(lis,pos):
	return max([1.0/abs(pos-x) for x in lis])
#gives proximity for all words
def wordPositionWeights(sentence,reference):
	sentence = sentence.lower()
	distMap={}
	referencePos = []
	count=0
	f1=open('stop.txt','r')
	stopFile=f1.read()
	table = string.maketrans("","")
	sentence=sentence.translate(table, string.punctuation)
	for word in sentence.split():
		count+=1
		if(word==reference):
			referencePos.append(count)
			pos = 0
	for word in sentence.split():
		pos+=1
		if(word==reference):
			continue
		if(word in distMap.keys() and distMap[word]>minDist(referencePos,pos)):
			distMap[word] = minDist(referencePos,pos)
		elif not( word in distMap.keys()):
			distMap[word] = minDist(referencePos,pos)
	for word in distMap.keys():
		if word in stopFile.split():
			del distMap[word]
	return distMap
#print wordPositionWeights(" Milky - definition of milky by The Free Dictionary","milky")
def get_from_docs(relevant):
	tf_list=[]
	print relevant
	print len(relevant)
	for result in relevant:
		tf_dict={}
		url=result['Url']
		#im=raw_input()
		#print result['Url']
		#page = requests.get(url)
		#htmlSource = page.text
		
		#browser = webdriver.Firefox()
		#browser.get(url)
		filename = wget.download(url)
		htmlSource = open(filename,'r').read()
		os.remove(filename)
		#print htmlSource
		soup=BeautifulSoup(htmlSource,'html5lib')
		for script in soup(["script", "style"]):
	    		script.extract()
		paras=soup.find_all(['p','title','b','i','h1','h2','h3','h4','h5','h6'])
		text=''
		for i in xrange(0,len(paras)):
			text=text + paras[i].get_text().encode('utf-8')
		lines = (line.strip() for line in text.splitlines())
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		text = '\n'.join(chunk for chunk in chunks if chunk)
		text=text.decode('unicode_escape').encode('ascii','ignore')
		table = string.maketrans("","")
		text=text.translate(table, string.punctuation)
		tf_dict=word_count(text)
		#print text
		#print tf_dict
		#inp = raw_input()
		if 'way' in tf_dict.keys():
			print tf_dict['way']
		tf_list.append(tf_dict)
		#title_text=result['Title']
		#title_text=title_text.decode('unicode_escape').encode('ascii','ignore')
		#print "Title Count:"
		#title_tf_dict=word_count(title_text)
	return tf_list

f = open('parseData5','r')
json_string =f.read()
my_map = json.loads(json_string)
results = my_map['d']['results']
relevant = []
irrelevant = []
cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True

for result in results:
	print "URL: " + result['Url'].encode('utf-8')
	print "Title: " + result['Title'].encode('utf-8')
	print "Description: " + result['Description'].encode('utf-8')
	print "Please give your feeedback[y|n]"
	#print wordPositionWeights(result['Title'].encode('utf-8'),'musk')
	my_inp = raw_input()
	#print tf_dict
	while(my_inp!='y' and my_inp!='n'):
		print "Human please enter valid feedback"
		my_inp = raw_input()
	if my_inp.lower()=='y':
		relevant.append(result)
	elif my_inp.lower()=='n':
		irrelevant.append(result)
tf_list = get_from_docs(relevant)
#sprint tf_list
scores=[]
#print tf_list
all_keys = []
for doc in tf_list:
	all_keys+=doc.keys()
#print all_keys
idf_scores = dict.fromkeys(list(set(all_keys)))
for key in all_keys:
	idf_scores[key]=0

for doc in tf_list:
	for key in all_keys:
		if(key in doc.keys()):
			idf_scores[key]+=doc[key]
# for doc in xrange(len(tf_list)):
# 	for key in tf_list[doc]:
# 		for d in xrange(len(tf_list)):
# 			if key in tf_list[d]:
# 				if not (key in idf_scores):idf_scores[key]=0
# 				idf_scores[key]=idf_scores[key]+tf_list[d][key]
# 			else:
# 				if not (key in idf_scores):idf_scores[key]=0
# 				idf_scores[key]=tf_list[doc][key]

idf_scores=collections.OrderedDict(sorted(idf_scores.items(), key=operator.itemgetter(1)))
print idf_scores
#print relevant
#print my_map['d']['results'][0]
