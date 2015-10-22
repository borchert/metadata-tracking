from fuzzywuzzy import fuzz
import ast

f = open("originator_values.txt","r")
o = f.read()
l = ast.literal_eval(o)

for i in l:
    term = i
    for j in l:
        print "fuzz.partial_ratio(\"" + term + "\", \"" + j + "\")"
        print fuzz.partial_ratio(term, j)
        """
        if partial_ratio > 70, store results in a dict for each 'term',
        which will give a starting point. Need to work on how to integrate
        into metadata processing. I'm thinking we create a master list to run against,
        then alter the XML val to match that. Would like to store the original somewhere,
        need to check ISO for an appropriate spot
        """