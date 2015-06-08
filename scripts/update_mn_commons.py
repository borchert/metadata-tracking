#! /usr/bin/env python
from __future__ import unicode_literals
__author__ = 'dykex005'

import json
import os
import shutil

GDRS_PATH = "//files.umn.edu/US/GIS-Spatial/GDRS"
MN_COMMONS_PATH = os.path.join("..", "mn-geospatial-commons")
GDRS_SHARE_PATH = os.path.join(".", "GDRS-share")
RESOURCES_PATH = os.path.join(GDRS_SHARE_PATH, "data", "pub")
PATH_TO_METADATA_XML = os.path.join("metadata", "metadata.xml")


if not os.path.exists(GDRS_SHARE_PATH):
    os.mkdir(GDRS_SHARE_PATH)

if not os.path.ismount(GDRS_SHARE_PATH):
    os.system("mount_smbfs {gdrs} {path}".format(gdrs=GDRS_PATH,
                                             path=GDRS_SHARE_PATH))

for root, dirs, files in os.walk(RESOURCES_PATH):
    if "metadata" in dirs:
        ds_name = root.split(os.path.sep)[-2] +"_"+ root.split(os.path.sep)[-1]
        if os.path.isfile(os.path.join(root, PATH_TO_METADATA_XML)):
            shutil.copyfile(os.path.join(root, 
                    PATH_TO_METADATA_XML), 
                os.path.join(MN_COMMONS_PATH, 
                    ds_name + ".xml"))
            print "copied {ds}".format(ds=ds_name)