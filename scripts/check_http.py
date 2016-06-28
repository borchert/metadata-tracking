#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import argparse
import os
import sys
import urllib2
import glob
from xml.etree import ElementTree as etree

def check_url(url):
    request = urllib2.Request(url)
    request.get_method = lambda : 'HEAD'
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code == 405:
            print "trying GET instead of HEAD"
            request.get_method = lambda : 'GET'
            response = urllib2.urlopen(request)
        elif e.code == 404:
            print  "     " + url, "is BAD! Code is 404"
            return
    code = response.getcode()
    if code == 200:
        return
    elif code == 202:
        print  "     " + url, "returned, should return 200 eventually"

def main():
    METADATA_OPTIONS = ['fgdc', 'mgmg', 'iso', 'eod', 'gdrs', 'guess']
    URL_XPATH = {"iso": "*//gmd:URL", "fgdc": "*//onlink", "mgmg": "*//onlink"}
    ISO_NSMAP = {
       "srv":"http://www.isotc211.org/2005/srv",
       "gco":"http://www.isotc211.org/2005/gco",
       "xlink":"http://www.w3.org/1999/xlink",
       "gts":"http://www.isotc211.org/2005/gts",
       "xsi":"http://www.w3.org/2001/XMLSchema-instance",
       "gml":"http://www.opengis.net/gml",
       "gmd":"http://www.isotc211.org/2005/gmd"
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("input_folder_path", help="indicate the path to the folder containing metadata with URLs to check.")
    parser.add_argument("metadata_type",help="Metadata standard used for input XMLs. Acceptable values are FGDC, MGMG, ISO, EOD, GDRS or GUESS (which takes a guess)")
    args = parser.parse_args()

    in_folder = args.input_folder_path
    if not os.path.isabs(in_folder):
        in_folder = os.path.abspath(os.path.relpath(in_folder,os.getcwd()))

    md = args.metadata_type.lower()
    if md not in METADATA_OPTIONS:
        sys.exit('Invalid metadata standard. Supported options are %s. Please try again.' % ( " ,".join(METADATA_OPTIONS)))


    xmls = glob.glob(os.path.join(in_folder, "*.xml"))

    url_path = URL_XPATH[md]

    for xml_path in xmls:
        xml_file_name = xml_path.split(os.path.sep)[-1]
        print "NOW ON FILE: " + xml_file_name

        xml_tree = etree.parse(xml_path)

        if md == "iso":
            links = xml_tree.findall(url_path, ISO_NSMAP)
        else:
            links = xml_tree.findall(url_path)

        #print links
        for link in links:
            #print link

            #import pdb; pdb.set_trace()

            #for now don't check zips, as I think it may generate all of them and will
            #probably annihilate servers
            try:
               # if link is not None and link.text is not None and ".zip" not in link.text:
                if link is not None and link.text is not None:
                    check_url(link.text)
            except TypeError as e:
                print e
                


if __name__ == "__main__":
    sys.exit(main())
