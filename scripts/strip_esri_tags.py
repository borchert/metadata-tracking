#!/usr/bin/env python 

import sys
import os
import shutil
from glob import glob
try:
    from lxml import etree
except ImportError:
    sys.exit("\n\nPython lib lxml not found. I need it! Maybe try `pip install lxml`")

def main():
    """
    Feed in a bunch of xml files, will strip Esri tags from each.
    """

    if len(sys.argv) != 2:
        sys.exit("I need a folder name!")
    
    xsl = etree.parse(os.path.join("xsl", "remove_ESRI_tags.xsl"))
    transform = etree.XSLT(xsl)

    
    folder = sys.argv[1]

    files = glob(os.path.join(folder, "*.xml"))
    
    for f in files:
        shutil.copyfile(f, os.path.join("..", "backup", f.split(os.path.sep)[-1]))
        tree = etree.parse(f)
        new_tree = transform(tree)
        new_tree.write(f)

if __name__ == "__main__":
    main()

