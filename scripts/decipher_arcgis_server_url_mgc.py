<<<<<<< HEAD
import arcpy
path_to_lyr = ""
group_lyr = arcpy.mapping.Layer(path_to_lyr)
for index, i in enumerate(arcpy.mapping.ListLayers(group_lyr)):     
    if i.visible:
        print index-1, i.longName
=======
print "importing arcpy"
import arcpy
print "done importing arcpy"
import os
import shutil
import zipfile
from glob import glob
import pdb

BASE_IN = r"C:\workspace\metadata-tracking\mn-geospatial-commons"
#BASE_OUT = r"C:\workspace\temp_gdrs"
"""
for root, dirs, files in os.walk(BASE_IN):
    if "ags_mapserver" in dirs:
        path_to_lyr = os.path.join(root, "ags_mapserver")
        g = glob(os.path.join(path_to_lyr, "*.lyr"))
        resource_name = os.path.split(root)[-1]
        print resource_name
        os.mkdir(os.path.join(BASE_OUT, resource_name))
        shutil.copyfile(os.path.join(root, "dataResource.xml"), os.path.join(BASE_OUT, resource_name, "dataResource.xml"))
        shutil.copyfile(os.path.join(root, "metadata", "metadata.xml"),  os.path.join(BASE_OUT, resource_name, "metadata.xml"))
        shutil.copyfile(g[0], os.path.join(BASE_OUT, resource_name, os.path.split(g[0])[-1]))
           
"""

path_to_lyr = ""
for root, dirs,files in arcpy.da.Walk(BASE_IN, datatype=["Layer"]):
    if len(files) > 0:
        for i in files:
            lyr = arcpy.mapping.Layer(os.path.join(root,i))
            if lyr.isGroupLayer:
                for index, ly in enumerate(arcpy.mapping.ListLayers(lyr)):     
                    if ly.visible:
                        #print lyr.serviceProperties["URL"] + "/" + ly.longName.replace("\\","/") + "/" + str(index-1)
                        layer_index_txt = open(os.path.join(root,"lyr_index"+str(index - 1)+".txt"), "wb")
                        layer_index_txt.write(str(index-1))
                        layer_index_txt.close()

>>>>>>> mn-geo-commons-ags-parse
