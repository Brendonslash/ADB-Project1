import urllib2
import base64
print "Enter your Web Query Human: "
inp = raw_input()
bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'+inp+'%27&$top=10&$format=json'
#Provide your account key here
accountKey = 'yaTtNJf/mq/VOXKXCliOjmUaeoL4hiK4akoPVAjvsdk'

accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}
req = urllib2.Request(bingUrl, headers = headers)
response = urllib2.urlopen(req)
content = response.read()
#content contains the xml/json response from Bing. 
print content
