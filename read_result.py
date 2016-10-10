# _*_ coding:utf-8 _*_
import json
import urllib
import urllib2
from bs4 import BeautifulSoup
import operator
import string
import requests
import collections
import os
import httplib2
from bing import execQuery
from urllib2 import urlopen
import requests
import numbers
import sys

#This function takes the html source text and returns a Ordered dictionary of words i.e the term frequency for each page
def word_count(string):
	my_string = string.lower().split()
	my_dict = {}
	
	#create a dict that contains each word in string as a key and the frequency of that word as its value
	for item in my_string:
		if item in my_dict:
			my_dict[item] += 1
		else:
			my_dict[item] = 1
	
	#remove stop-words	
	f1=open('stop.txt','r')
	stopFile=f1.read()
	for word in stopFile.split():
		if  word in my_dict:
			del my_dict[word]
			
	#remove words that are already present in the query
	for word in my_query.split():
		if  word in my_dict:
			del my_dict[word]
			
	#convert into a sorted dict and return it
	sorted_dict = collections.OrderedDict(sorted(my_dict.items(), key=operator.itemgetter(1)))
	return sorted_dict

#Takes list of relevant documents and returns a list which contains dicts of term frequencies for each 'relevant' web page
def get_from_docs(relevant):
	tf_list=[]

	#Getting only text-web pages 
	for result in relevant:
		tf_dict={}
		url=result['Url']
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		try:
			response = opener.open(url)
			info = response.info()
			if 'text' not in (info.dict['content-type']):      
				continue
		except:
			continue
			
		#Taking text only from selected HTML tags
		infile = opener.open(url)
		page = infile.read()
		soup=BeautifulSoup(page,'html.parser')
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
		try:
			text=text.decode('unicode_escape').encode('ascii','ignore')
		except:
			continue
		#Removing punctuations
		table = string.maketrans("","")
		text=text.translate(table, string.punctuation)
		
		#call word_count function to return an ordered dict of words for this webpage, 
		#and append it to the list of dicts for each relevant page.
		tf_dict=word_count(text)
		tf_list.append(tf_dict)
	return tf_list

#flag is a boolean to exit the loop
flag=True
args = sys.argv
authKey = ''
precision_threshold = 0
my_query = ''
#Handle incorrect calls
try:
	authKey  = args[1]
	precision_threshold = float(args[2])
	my_query = args[3]
except:
	"Human the usage is python read_result.py key precision@k query"
	pass

#t_word is a list of words in titles and descriptions of all relevant pages, that have first letter capitalised.
t_word=[]
Round=1
while(flag):
	print "Round "+ str(Round)
	print "Parameters: " 
	print "Client Key = " + authKey
	print "Query = " + my_query
	print "Precision = " + str(precision_threshold)
	try:
		alpha=execQuery(my_query,authKey)
		print "URL: " + alpha[0]
	except:
		print "Authentication Error. Is your key correct?"
	
	#alpha[1] contains the content returned by execQuery in bing.py
	json_string = alpha[1]
	my_map = json.loads(json_string)
	results = my_map['d']['results']
	relevant = []
	irrelevant = []
	precision=0
	print "Total Number of results : "+str(len(results))
	
	#Handle the case that bing returns <10 results
	if len(results) < 10:
		print "Program Terminated. Results returned were less than 10"
		break
	else:
		print "Bing Search Results:"
		print "===================="
		counter = 1
		for result in results:
			print "Result "+ str(counter)
			print "["
			print "  URL: " + result['Url'].encode('utf-8')
			print "  Title: " + result['Title'].encode('utf-8')
			print "  Description: " + result['Description'].encode('utf-8')
			print "]"
			print "Relevant (Y/N)?"
			my_inp = raw_input()
			while(my_inp!='y' and my_inp!='n'):
				print "Human please enter valid feedback"
				my_inp = raw_input()
			if my_inp.lower()=='y':
				precision+=1
				relevant.append(result)
			elif my_inp.lower()=='n':
				irrelevant.append(result)
			counter+=1
		#function get_from_docs returns a list of dicts of term frequencies all 'relevant' web pages
		tf_list = get_from_docs(relevant)
		
		#Combine the list of dicts into one single dict, adding up values of same key values.
		scores=[]
		all_keys = []
		for doc in tf_list:
			all_keys+=doc.keys()
		term_frequency = dict.fromkeys(list(set(all_keys)))
		for key in all_keys:
			term_frequency[key]=0
		
		for doc in tf_list:
			for key in all_keys:
				if(key in doc.keys()):
					term_frequency[key]+=doc[key]

		term_frequency=collections.OrderedDict(sorted(term_frequency.items(), key=operator.itemgetter(1)))
		title_string=''
		desc_string=''
		for result in relevant:
			title_string+=result['Title']
			desc_string+=result['Description']
		

		td_terms_list=[]
		title_append1=''
		title_append2=''
		td_word_frequency=collections.OrderedDict()
		if(len(term_frequency)!=0):
			if term_frequency.items()[len(term_frequency)-1][1] < 7:
				table = string.maketrans("","")
				#handle unicode characters
				td_lines=(title_string.encode('utf-8') + " " + desc_string.encode('utf-8')).lower()
				#remove punctuations
				td_lines=td_lines.translate(table, string.punctuation)
				td_words=td_lines.split()
				f3=open('stop.txt','r')
				stopFile=f3.read()
				#remove stop-words
				td_words = list(filter(lambda x: x not in stopFile.split(),td_words))
				for word in td_words:
					if not(word.isdigit()):
						td_terms_list.append(word)
				td_string=' '.join(td_terms_list)
				td_word_frequency=word_count(td_string)
				title_append1=td_word_frequency.items()[len(td_word_frequency)-1][0]
				title_append2=td_word_frequency.items()[len(td_word_frequency)-2][0]
		
		else: 
			print "Program terminated."
			break	

	max=0
	title_word=''
	f=open('stop.txt','r')	
	stopFile=f.read()
	for word in title_string.encode('utf-8').split() + desc_string.encode('utf-8').split():
		#Remove punctuation
		table = string.maketrans("","")
		word = word.translate(table, string.punctuation)
		#word should not be a digit, first letter should be capital, and should not occur in the query or stop-words
		if word!="" and word[0].isupper() and word.lower() not in my_query.lower() and word.lower() not in stopFile.split():
			t_word.append(word)
		if word.decode('utf-8') in term_frequency.keys() and not(word.isdigit()) and term_frequency[word] > max:
			max = term_frequency[word]
			title_word=word
	
	#find most frequent word with first letter capitalised in the titles and descriptions of all of the relevant documents
	most_frequent_count = 0
	most_frequent_word = t_word[0]
	for caps in t_word:
		if (caps.lower() in term_frequency.keys()) and (term_frequency[caps.lower()] > most_frequent_count):
			most_frequent_word = caps
			most_frequent_count = term_frequency[caps.lower()]
	i=1
	while(i<len(term_frequency)):
		append1=term_frequency.items()[len(term_frequency)-i][0]
		i+=1
		#word should not be a digit,  should not occur in the query and should not be the same as the one taken from title/description
		if not(append1.isdigit()) and (append1 != title_word) and (append1 not in my_query) and (append1 != most_frequent_word.lower()):
			break
	i=1	
	while(i<len(term_frequency)):
		append2=term_frequency.items()[len(term_frequency)-i-1][0]
		i+=1
		#word should not be a digit,  should not occur in the query and should not be the same as the one taken from title/description
		if not(append2.isdigit()) and (append2 != title_word) and (append2 not in my_query) and (append2 != most_frequent_word.lower()):
			break		
	print "==========================================================="
	aug = []
	my_query_old = my_query
	if(len(term_frequency)!=0):
		if term_frequency.items()[len(term_frequency)-1][1] >= 10:
			aug.append(append1)
			aug.append(most_frequent_word.lower())
			my_query = my_query + " "+ append1 + " " + most_frequent_word.lower()
		#If not enough content from HTML of the pages, use only titles and descriptions
		if term_frequency.items()[len(term_frequency)-1][1] < 10:
			aug.append(title_append1)
			aug.append(title_append2)
			my_query=my_query + " " + title_append1 + " " + title_append2
	
	else:
		print "No results returned"
		break
	precision=precision*1.0/10
	print "FEEDBACK SUMMARY"
	print "Query " + my_query_old
	print "Precision " + str(precision)
	Round+=1
	if precision >= precision_threshold: 
		flag=False
		print "Desired Precision reached, done"
	else:
		print "Still below desired precision of "+ str(precision_threshold)
		print "Augmenting by " + aug[0] +" "+ aug[1]
	
	


