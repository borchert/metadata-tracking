import requests
import os
import pdb

lyrs = []
START_PATH = "."

#build list of all lyr_text files
for path, dirs, files in os.walk(START_PATH):
    if "lyr_text.txt" in files:
        lyrs.append(os.path.join(path, "lyr_text.txt"))

for i, f in enumerate(lyrs):
    print ("####################")
    resource_name = os.path.split(f)[0].lstrip(START_PATH + os.path.sep)
    print resource_name
    with open(f, "r") as lyr_text:
        lyrs = lyr_text.readlines()
        print str(len(lyrs))
