#!/usr/bin/env python 

import sys
import os
try:
    from lxml import etree
except ImportError:
    sys.exit("\n\nPython lib lxml not found. I need it! Maybe try `pip install lxml`")

def main():
    """
    Feed in a bunch of xml files, will rewrite each pretty printed.
    """

    if len(sys.argv) < 2:
        sys.exit("I need a file name!")
    
    files = sys.argv[1:]
    
    for f in files:
        tree = etree.parse(f)
        tree.write(f, pretty_print=True)

if __name__ == "__main__":
    main()

