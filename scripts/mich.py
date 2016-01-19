#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import etree
import requests
from bs4 import BeautifulSoup
from copy import deepcopy
import os, os.path
import json
import pdb
import re
import datetime
from operator import itemgetter
import pprint

from scrape_open_data import request_data_json, get_list_of_datasets

j = request_data_json("http://gis.michigan.opendata.arcgis.com/data.json")
datasets = get_list_of_datasets(j)
datasets_json = []
for i in datasets:
    r = requests.get(i)
    p = r.json()["data"]["main_group_title"]
    datasets_json.append(p)
    d = set(datasets_json)
    print d
