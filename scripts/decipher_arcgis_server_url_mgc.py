import arcpy
path_to_lyr = ""
group_lyr = arcpy.mapping.Layer(path_to_lyr)
for index, i in enumerate(arcpy.mapping.ListLayers(group_lyr)):     
    if i.visible:
        print index-1, i.longName