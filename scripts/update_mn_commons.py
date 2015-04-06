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
    docs = []
    solr = ogp2solr.SolrOGP()
    for dataset_id in datasets:
        print datasets[dataset_id]["dsBaseName"]
        doc = md2ogp.GDRSDocument(datasets[dataset_id],
            dataset_id.replace("{","").replace("}",""), 
            None, 
            None)
        ogp_tree = md2ogp.write_ogp_tree(doc)
        docs.append(ogp_tree)
    solr.add_to_solr_bulk(docs)