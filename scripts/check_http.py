import urllib2
url = "http://opendata.minneapolismn.gov/datasets/8c97cfb0700b4c8b929459dc5744efc3_0.zip"
request = urllib2.Request(url)
request.get_method = lambda : 'HEAD'
response = urllib2.urlopen(request)

code = response.getcode()
if code == 200:
    print url, "is OK!"
elif code >= 400:
    print url, "is BAD! Code is", code
elif code == 202:
    print url, "returned, should return 200 eventually" 