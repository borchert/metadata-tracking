#!/usr/bin/env python 

import sys
import os
from glob import glob
try:
    from lxml import etree
except ImportError:
    sys.exit("\n\nPython lib lxml not found. I need it! Maybe try `pip install lxml`")

def main():
    """
    Feed in a bunch of xml files and I will rewrite each pretty printed.
    I don't check for anything, so I really trust you to do the right thing
    and only feed me actual file names.
    """

    if len(sys.argv) < 2:
        sys.exit("I need a path to a folder!")
    
    folder = sys.argv[1]
    files_list = []
    for root,dirs,files in os.walk(folder):
        files_list = files_list + glob(os.path.join(root, "*.xml"))
    
    for f in files_list:
        tree = etree.parse(f)
        tree.write(f, pretty_print=True)

if __name__ == "__main__":
    main()

