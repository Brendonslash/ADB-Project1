import urllib2
import base64
#print "Enter your Web Query Human: "

def execQuery(inp):
	#To handle spaces in the query
# 	if inp == "": 
# 		print "Enter the query:"
# 		inp = raw_input()
	inp = inp.replace(" ","%20")
	#rint inp
	bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'+inp+'%27&$top=10&$format=json'
	#print bingUrl
	#Provide your account key here
	accountKey = 'yaTtNJf/mq/VOXKXCliOjmUaeoL4hiK4akoPVAjvsdk'

	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()
	#content contains the xml/json response from Bing. 
# 	print content
	return content

# inp = raw_input()
# execQuery(inp)