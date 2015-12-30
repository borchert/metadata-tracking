#! /usr/bin/env python
from __future__ import unicode_literals
__author__ = 'dykex005'

import json
import os
import shutil
from glob import glob

GDRS_PATH = "//files.umn.edu/US/GIS-Spatial/GDRS"
MN_COMMONS_PATH = os.path.join("..", "mn-geospatial-commons")
#GDRS_SHARE_PATH = os.path.join(".", "GDRS-share")
GDRS_SHARE_PATH = r"V:\\"
RESOURCES_PATH = os.path.join(GDRS_SHARE_PATH, "data", "pub")
PATH_TO_METADATA_XML = os.path.join("metadata", "metadata.xml")
PATH_TO_DATA_RESOURCE_XML = "dataResource.xml"

def copy_file(root, in_path, out_path):
    if os.path.isfile(os.path.join(root, in_path)):
        shutil.copyfile(os.path.join(root,
            in_path),
            os.path.join(out_path,
            os.path.split(in_path)[-1])
        )

    
if not os.path.exists(GDRS_SHARE_PATH):
    os.mkdir(GDRS_SHARE_PATH)

if not os.path.ismount(GDRS_SHARE_PATH):
    os.system("mount_smbfs {gdrs} {path}".format(gdrs=GDRS_PATH,
                                             path=GDRS_SHARE_PATH))

for root, dirs, files in os.walk(RESOURCES_PATH):
    if "metadata" in dirs:
        ds_name = root.split(os.path.sep)[-2] +"_"+ root.split(os.path.sep)[-1]
        out_path = os.path.join(MN_COMMONS_PATH, ds_name)
        if not os.path.isdir(out_path):
            os.mkdir(out_path)
        copy_file(root, PATH_TO_METADATA_XML, out_path)
        copy_file(root, PATH_TO_DATA_RESOURCE_XML, out_path)
        if "ags_mapserver" in dirs:
            path_to_ags_dir = os.path.join(root, "ags_mapserver")
            g = glob(os.path.join(path_to_ags_dir, "*.lyr"))
            if len(g) > 0:
                path_to_lyr = g[0]
                copy_file(root, path_to_lyr, out_path)
        print "copied {ds}".format(ds=ds_name)
     
#TODO remove these and wrap this script in bat/sh files
#os.system("./remove_BOM_folder.py ../mn-geospatial-commons")
#os.system("./prettify_folder.py ../mn-geospatial-commons")
