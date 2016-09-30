# _*_ coding:utf-8 _*_
import json
import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import lxml
from lxml.html.clean import Cleaner
import operator
import string
import requests
import collections
import wget
import os
import httplib2
from bing import execQuery
from nltk.stem.wordnet import WordNetLemmatizer

#gives frequency
def word_count(string):
	lemtzr = WordNetLemmatizer()
	my_string = string.lower().split()
	my_dict = {}
	for item in my_string:
		item = lemtzr.lemmatize(str(item))
		if item in my_dict:
			my_dict[item] += 1
		else:
			my_dict[item] = 1
	f1=open('stop.txt','r')
	stopFile=f1.read()
	for word in stopFile.split():
		if  word in my_dict:
			del my_dict[word]
	for word in my_query.split():
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
	#print relevant
	#print len(relevant)
	for result in relevant:
		tf_dict={}
		url=result['Url']
# 		print url
# 		url=getContentLocation(url)
# 		print "Redirected:",
# 		print url
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
		soup=BeautifulSoup(htmlSource,'html.parser')
		for script in soup(["script", "style"]):
	    		script.extract()
		paras=soup.find_all(['p','title','b','i','h1','h2','h3','h4','h5','h6'])
		text=''
		for i in xrange(0,len(paras)):
			text=text + paras[i].get_text().encode('utf-8')
		#Handling unicode characters	
		lines = (line.strip() for line in text.splitlines())
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		text = '\n'.join(chunk for chunk in chunks if chunk)
		text=text.decode('unicode_escape').encode('ascii','ignore')
		#Removing punctuations
		table = string.maketrans("","")
		text=text.translate(table, string.punctuation)
		tf_dict=word_count(text)
		#print text
		#print tf_dict
		#inp = raw_input()
		# if 'way' in tf_dict.keys():
# 			print tf_dict['way']
		tf_list.append(tf_dict)
		#Take words from title
		#title_text=result['Title']
		#title_text=title_text.decode('unicode_escape').encode('ascii','ignore')
		#print "Title Count:"
		#title_tf_dict=word_count(title_text)
	return tf_list

flag=True
print "Input Query:"
my_query=raw_input().lower()
print "Input required precision between 0 and 1:"
precision_threshold=float(raw_input())
while(flag):	
	json_string=execQuery(my_query)
	# f = open('parseData5','r')
	# json_string =f.read()
	my_map = json.loads(json_string)
	results = my_map['d']['results']
	relevant = []
	irrelevant = []
	precision=0

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
			precision+=1
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
	term_frequency = dict.fromkeys(list(set(all_keys)))
	for key in all_keys:
		term_frequency[key]=0
	
	for doc in tf_list:
		for key in all_keys:
			if(key in doc.keys()):
				term_frequency[key]+=doc[key]
	# for doc in xrange(len(tf_list)):
	# 	for key in tf_list[doc]:
	# 		for d in xrange(len(tf_list)):
	# 			if key in tf_list[d]:
	# 				if not (key in term_frequency):term_frequency[key]=0
	# 				term_frequency[key]=term_frequency[key]+tf_list[d][key]
	# 			else:
	# 				if not (key in term_frequency):term_frequency[key]=0
	# 				term_frequency[key]=tf_list[doc][key]

	term_frequency=collections.OrderedDict(sorted(term_frequency.items(), key=operator.itemgetter(1)))
	title_string=''
	desc_string=''
	for result in relevant:
		title_string+=result['Title']
		desc_string+=result['Description']
	
	max=0
	title_word=''	
	#print title_string.encode('utf-8') + desc_string.encode('utf-8')
	for word in title_string.encode('utf-8').split() + desc_string.encode('utf-8').split():
		if word in term_frequency.keys() and not(word.isdigit()) and term_frequency[word] > max:
			#print word
			max = term_frequency[word]
			title_word=word

	td_terms_list=[]
	title_append1=''
	title_append2=''
	#print term_frequency.items()[len(term_frequency)-1][1]
	if(len(term_frequency)!=0):
		if term_frequency.items()[len(term_frequency)-1][1] < 7:
			table = string.maketrans("","")
		#print title_word
		
			td_lines=(title_string.encode('utf-8') + " " + desc_string.encode('utf-8')).lower()
			print td_lines
			td_lines=td_lines.translate(table, string.punctuation)
	
			td_words=td_lines.split()
			#print td_words
			f3=open('stop.txt','r')
			stopFile=f3.read()
			td_words = list(filter(lambda x: x not in stopFile.split(),td_words))
			for word in td_words:
				if not(word.isdigit()):
					td_terms_list.append(word)
			td_string=' '.join(td_terms_list)
			td_word_frequency=word_count(td_string)
			print td_word_frequency
			title_append1=td_word_frequency.items()[len(td_word_frequency)-1][0]
			title_append2=td_word_frequency.items()[len(td_word_frequency)-2][0]
	
	else: 
		print "No Results Returned by Bing!"
		break	
	#print td_terms_list
	#print title_append1
	i=1
	while(i<len(term_frequency)):
		append1=term_frequency.items()[len(term_frequency)-i][0]
		i+=1
		if not(append1.isdigit()) and (append1 != title_word) and (append1 not in my_query):
			break
		
	while(i<len(term_frequency)):
		append2=term_frequency.items()[len(term_frequency)-i-1][0]
		i+=1
		if not(append2.isdigit()) and (append2 != title_word) and (append2 not in my_query):
			break
				
			
			
	#print append1, append2
	if(len(term_frequency)!=0):
		if term_frequency.items()[len(term_frequency)-1][1] >= 10:
			my_query = my_query + " "+ append1 + " " + append2 #+ " " + title_word
		if term_frequency.items()[len(term_frequency)-1][1] < 10:
			my_query=my_query + " " + title_append1 + " " + title_append2
	
	else:
		print "No results returned"
		break
	
	#print term_frequency
	print "New Query is:",
	print my_query
	precision=precision*1.0/10
	print precision
	if precision >= precision_threshold: flag=False
	#print relevant
	#print my_map['d']['results'][0]
	
	#TODO: Catch errors, terminate on 0, clean code, refactor, testing
	#TODO: take from title only in second iteration
	#TODO: order is important
	#TODO: Sergey Brin
	#TODO: Noun with capital letter in first iteration


