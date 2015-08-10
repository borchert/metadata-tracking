#!/usr/bin/env python

import sys
import os
import codecs
from glob import glob

def main():
    """
    Feed in a bunch of xml files and I will remove the BOM from each if it is there.
    """

    if len(sys.argv) < 2:
        sys.exit("I need a path to a folder!")

    folder = sys.argv[1]

    files = glob(os.path.join(folder, "*.xml"))

    for f in files:
        opened_file = open(f, "r")
        contents = opened_file.read()
        if contents[:3] == codecs.BOM_UTF8:
            print "found BOM in {name}".format(name=f)
            contents = contents[3:]
        opened_file.close()
        write_file = open(f, "w")
        write_file.write(contents)
        write_file.close()


if __name__ == "__main__":
    main()
