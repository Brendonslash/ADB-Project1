from py_bing_search import PyBingWebSearch
search_term = "Milky"
bing_web = PyBingWebSearch('yaTtNJf/mq/VOXKXCliOjmUaeoL4hiK4akoPVAjvsdk', search_term, web_only=False)
first_ten_result= bing_web.search(limit=10, format='json')
print (first_ten_result[0])
