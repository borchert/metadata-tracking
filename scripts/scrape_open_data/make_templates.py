#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
import codecs
import string
import pdb
import os

fpath = os.path.abspath(__file__)
path = os.path.dirname(fpath)

TEMPLATE_SOURCE_FILE_NAME = os.path.join(path, "template_info.csv")

base_template = codecs.open(os.path.join(path, "_opendata_iso_template.xml"), "rU", "utf-8")
base_string = base_template.read()

class CustomFormatter(string.Formatter):
    def get_value(self,key, args, kwargs):
        if kwargs.has_key(key):
            return kwargs[key]
        else:
            print "Leaving key in template: " + key
            return "{" + key + "}"
    def check_unused_args(self,used_args, args, kwargs):
        return


with open(TEMPLATE_SOURCE_FILE_NAME, "rU") as template_info:
    reader = csv.DictReader(template_info)
    for row in reader:
        output_template_name = row.pop('output_template_name')
        output_template_string = CustomFormatter().format(base_string, **row)
        output_file = codecs.open(os.path.join(path, output_template_name), "w", "utf-8")
        output_file.write(output_template_string)
        output_file.close()
