import urllib2
import base64

def execQuery(inp,key):
	#replace space by %20 in the query
	inp = inp.replace(" ","%20")
	bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'+inp+'%27&$top=10&$format=json'
	accountKey = key
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	#content contains the xml/json response from Bing.
	content = response.read() 
	return (bingUrl,content)
