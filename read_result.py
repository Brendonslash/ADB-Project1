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
	sorted_dict = sorted(my_dict.items(), key=operator.itemgetter(1))
	print(sorted_dict)

f = open('parseData','r')
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
	my_inp = raw_input()
	url=result['Url']
	#url='http://en.wikipedia.org/wiki/Milky_Way'
	response=urllib2.urlopen(url)
	htmlSource=response.read()
	#htmlSource=lxml.html.tostring(cleaner.clean_html(lxml.html.XML(url)))
	soup=BeautifulSoup(htmlSource,'html5lib')
	for script in soup(["script", "style"]):
    		script.extract()
	paras=soup.find_all(['p','title','b','i'])
	text=''
	for i in xrange(0,len(paras)):
		text=text + paras[i].get_text().encode('utf-8')
	lines = (line.strip() for line in text.splitlines())
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	text = '\n'.join(chunk for chunk in chunks if chunk)
	text=text.decode('unicode_escape').encode('ascii','ignore')
	table = string.maketrans("","")
	text=text.translate(table, string.punctuation)
	word_count(text)
	title_text=result['Title']
	title_text=title_text.decode('unicode_escape').encode('ascii','ignore')
	print "Title Count:"
	word_count(title_text)
	while(my_inp!='y' and my_inp!='n'):
		print "Human please enter valid feedback"
		my_inp = raw_input()
	if my_inp.lower()=='y':
		relevant.append(result)
	elif my_inp.lower()=='n':
		irrelevant.append(result)
#print relevant
#print my_map['d']['results'][0]

