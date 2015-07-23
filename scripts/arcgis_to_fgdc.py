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
    Feed in a bunch of xml files, if in Esri standard will transform to ISO 19139
    """

    if len(sys.argv) != 2:
        sys.exit("I need a folder name!")

    xsl = etree.parse(os.path.join("xsl", "ArcGIS2FGDC.xsl"))
    transform = etree.XSLT(xsl)


    folder = sys.argv[1]

    files = glob(os.path.join(folder, "*.xml"))

    for f in files:
        tree = etree.parse(f)
        shutil.copyfile(f, os.path.join("..", "backup", f.split(os.path.sep)[-1]))
        new_tree = transform(tree)
        new_tree.write(f, pretty_print=True)

if __name__ == "__main__":
    main()
