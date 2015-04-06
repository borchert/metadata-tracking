#! /usr/bin/env python
from __future__ import unicode_literals
__author__ = 'dykex005'
PATH_TO_OGP_MDT_SRC = "/Users/dykex005/Workspace/OGP-metadata-py/src"
import sys
sys.path.append(PATH_TO_OGP_MDT_SRC)
import md2ogp
import json
import ogp2solr
import urllib2
import os.path

MANIFEST_URL = "ftp://ftp.gisdata.mn.gov/pub/gdrs/system/metadata/manifest.json"
OUTPUT_PATH = "../mn-geospatial-commons"

try:
    req = urllib2.urlopen(MANIFEST_URL)
except URLError as e:
    if hasattr(e, 'reason'):
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    elif hasattr(e, 'code'):
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
else:
    manifest = json.loads(req.read())
    datasets = manifest["dsDetails"]
    for dataset_id in datasets:
        print datasets[dataset_id]["dsBaseName"]
        if datasets[dataset_id]["dsMetadataUrl"]:
            metadata_url = datasets[dataset_id]["dsMetadataUrl"].rstrip(".html")+".xml"
            metadata_filename = metadata_url.split("/")[-3]+".xml"

            with open(os.path.join(OUTPUT_PATH, metadata_filename), "wb") as metadata_file: 
                try:
                    r = urllib2.urlopen(metadata_url)
                except URLError as e:
                    if hasattr(e, 'reason'):
                        print 'We failed to reach a server.'
                        print 'Reason: ', e.reason
                    elif hasattr(e, 'code'):
                        print 'The server couldn\'t fulfill the request.'
                        print 'Error code: ', e.code
                else:
                    metadata_file.write(r.read())