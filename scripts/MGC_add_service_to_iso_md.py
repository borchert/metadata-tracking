import requests
import os
import pdb
from lxml import etree

lyrs = []
resources = []
START_PATH = "/Users/dykex005/metadata/mn-geospatial-commons"
ISO_MD_PATH = "/Users/dykex005/Workspace/CIC-GDDP/edu.umn/Minnesota_Geospatial_Commons/2_metadata_transition"
ONLINE_RESOURCE_XSLT_PATH = "/Users/dykex005/Workspace/mgc-iso/online_resource.xsl"

#build list of all lyr_text files
for path, dirs, files in os.walk(START_PATH):
    if "lyr_text.txt" in files:
        resources.append(os.path.split(path)[-1])
        lyrs.append(os.path.join(path, "lyr_text.txt"))

xslt_root = etree.parse(ONLINE_RESOURCE_XSLT_PATH)
transform = etree.XSLT(xslt_root)

for index, res in enumerate(resources):
    print index,res
    metadata = etree.parse(os.path.join(ISO_MD_PATH, res + "_iso.xml"))
    result_metadata = transform(metadata, url="foo", protocol="bar")
    print result_metadata
    result_metadata.write(os.path.join(ISO_MD_PATH, res + "_iso.xml.test.xml"))
