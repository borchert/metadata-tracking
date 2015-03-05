import os
import json
import pdb
from lxml import etree

#don't enter these dirs (at the root level)
IGNORE_DIRS = ["scripts", "testing", ".git", "inbox"]

#{id: path}
layers = {}

def get_metadata_standard(root):
    root_element_name = root.getroot().tag
    if root_element_name == "metadata":
        if "Minnesota" in root.find("metainfo/metstdn").text:
            return "mgmg"
        elif "FGDC" in root.find("metainfo/metstdn").text:
            return "fgdc"
    elif root_element_name.find("MD_Metadata") != -1:
        return "iso"

with open("layers.json", "wb") as layers_json_file:

    for dirpath, dirs, files in os.walk("."):

        files = [f for f in files if not f[0] == '.' and f[-4:] == '.xml']
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for f in files:
            tree = etree.parse(os.path.join(dirpath, f))
            standard = get_metadata_standard(tree)

            if standard == "mgmg" or standard == "fgdc":
                layer_id = tree.find("idinfo/citation/citeinfo/title").get("catid")
               
            elif standard == "iso":
                NSMAP = {
                   "srv":"http://www.isotc211.org/2005/srv",
                   "gco":"http://www.isotc211.org/2005/gco",
                   "xlink":"http://www.w3.org/1999/xlink",
                   "gts":"http://www.isotc211.org/2005/gts",
                   "xsi":"http://www.w3.org/2001/XMLSchema-instance",
                   "gml":"http://www.opengis.net/gml",
                   "gmd":"http://www.isotc211.org/2005/gmd"
                }
                layer_id = tree.findtext("gmd:fileIdentifier/gco:CharacterString", "UNKNOWN", NSMAP)

            if layer_id is not "UNKNOWN" and layer_id is not None:
                layers[layer_id] = os.path.join(dirpath.lstrip("./"), f)

    layers_json_file.writelines(json.dumps(layers, indent=4))

