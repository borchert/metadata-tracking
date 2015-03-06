"""
Writes a csv file containing the urls of metadata files from the Minnesota Geospatial Commons
"""

import urllib2
import json
import csv

CKAN_URL = "http://gisdata.mn.gov/api/3/action/"

def get_urls():
    with open("mgc-urls.txt", "w") as f:
        url_list = []
        #get package list
        response = urllib2.urlopen(CKAN_URL + "package_list")
        r = response.read()
        plist_req = json.loads(r)

        if plist_req['success']:
            plist = plist_req['result']
        else:
            print 'package list error'
            print plist_req['error']
            plist = []

        for p in plist[:4]:
            response = urllib2.urlopen(CKAN_URL + "package_show?id=" + p)
            r = response.read()
            resp = json.loads(r)

            #parse response
            if resp["success"]:
                ex = resp['result']['extras']
                md = [i for i in ex if i['key'] == 'dsMetadataUrl']
                if len(md) >0:
                    url = md[0]['value']
                    print(url)
                    url_list.append(url+"\n")

        f.writelines(url_list)

get_urls()
