import requests
from fuzzywuzzy import process
import os
import pdb

lyrs = []
START_PATH = "."

# This script was used to read lyr_text files for each mn commons resources
# and match layers from the mapservice (commons only goes to mapservice level,
# but we want individual layer level for geoblacklight/ogp) 

#build list of all lyr_text files
for path, dirs, files in os.walk(START_PATH):
    if "lyr_text.txt" in files:
        lyrs.append(os.path.join(path, "lyr_text.txt"))

for i, f in enumerate(lyrs):
    print ("####################")
    with open(f, "r") as lyr_text:
        lyrs = lyr_text.readlines()

        for i in lyrs:
            print i.rstrip("\n")
            if i.startswith("Root") and len(lyrs) > 1:
                lyrs.remove(i)

            elif i.startswith("Root") or i.startswith("UnmatchedService") and len(lyrs) == 1:
                url = i.split("|||")[-1].rstrip("\n")
                resource_name = os.path.split(f)[0].lstrip(START_PATH + os.path.sep)
                r = requests.get(url+"?f=json")

                if r.status_code == 200:
                    rj = r.json()

                    if rj.has_key("layers"):
                        layers_dict = {lyr["name"]: lyr["id"] for lyr in rj["layers"]}
                        match = process.extractOne(resource_name, layers_dict.keys())
                        print resource_name, match
                        go_ahead = raw_input("Match? (Y/N/O): ")

                        if go_ahead.lower() == "y":
                            lyr_index = layers_dict[match[0]]
                            lyrs.append("MatchedService|||" + url.rstrip("/") + "/" + str(lyr_index) +"\n")
                            lyrs.remove(i)
                        elif go_ahead.lower() == "o":
                            new_url = raw_input("Enter service url: ")
                            lyrs.append("MatchedService|||" + new_url + "\n")
                        else:
                            lyrs.append("UnmatchedService|||" + url.rstrip("/") + "\n")
                            lyrs.remove(i)

            elif i.startswith("UnmatchedService") and len(lyrs) == 2:
                url = i.split("|||")[-1].rstrip("\n")
                resource_name = os.path.split(f)[0].lstrip(START_PATH + os.path.sep)
                ok = raw_input("OK to remove? (Y/N)")
                if ok.lower() == "y":
                    lyrs.remove(i)


        lyr_text_write = open(f,"wb")
        lyr_text_write.writelines(lyrs)
        lyr_text_write.close()
