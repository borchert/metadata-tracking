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

"""
Script for writing ISO 19139 metadata for Esri Open Data datasets. Work in progress...
"""

def get_list_of_datasets(root_data_json):
    return [i.identifier for i in root_data_json]


def request_data_json(url):
    try:
        print "requesting data.json..."
        j = requests.get(url).json()
        print "data.json received..."
    except requests.exceptions.HTTPError as e:
        sys.exit(e.message)
    else:
        return j["dataset"]


def get_data_json(url):
    return request_data_json(url)


def get_elements_for_open_data(tree):
    field_map = {}
    for field in FIELDS:
        field_map[field] = tree.findall(PATHS[field],NSMAP)
    return field_map


def parse_template_into_tree(template_name="scrape_open_data/opendata_iso_template_gmd_gone.xml"):
    return etree.parse(template_name)


def get_bbox(dataset):
    """
    Function that reads a dataset record from data.json and if the key 'spatial' exists, splits
    it into a list and returns it. If 'spatial' is null or equivalent to a global scale, returns False
    """
    # we don't want null bboxes or "global" datasets, which are most likely just incorrect bboxes
    if not dataset["spatial"] or dataset["spatial"] == "-180.0,-90.0,180.0,90.0":
        return False
    else:
        return dataset["spatial"].split(",")


def get_dataset_json(dataset_id):
    try:
        r = requests.get(dataset_id + ".json")
    except requests.exceptions.HTTPError as e:
        sys.exit(e.message)
    else:

        if "json" in r.headers["content-type"]:
            json = r.json()
            return json["data"]


def parse_datatype(dataset_detail):
    try:
        geometryType = dataset_detail["geometry_type"]
    except (KeyError,TypeError) as e:
        print "couldn't get geometry type for {title}".format(title=dataset["title"])
        return "undefined"

    if geometryType == "esriGeometryPoint" or geometryType == "esriGeometryMultipoint":
        return "point"

    elif geometryType == "esriGeometryPolyline":
        return "curve"

    elif geometryType == "esriGeometryPolygon" or geometryType == "esriGeometryEnvelope":
        return "surface"
    else:
        return "nonspatial"

def get_date_tag_from_code_tag(code_tag):
    for element in code_tag.getparent().getparent().getchildren():
        if element.tag == "{http://www.isotc211.org/2005/gmd}date":
            return element

def main(url, prefix, output_path, template):
    """
        url = Esri Open Data root url (like opendata.minneapolismn.gov)
        prefix = what to put in front of each file name that gets written out
        output_path = where output files should be written
    """

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    if not url.endswith("data.json"):
        url = url.rstrip("/") + "/data.json"

    data_json = get_data_json(url)

    for dataset in data_json:

        if dataset["webService"].endswith(".pdf"):
            print "skipping {d} cuz it's a PDF!".format(d=dataset['title'])
            continue

        dataset_detail = get_dataset_json(dataset["identifier"])
        print "Now on:", dataset_detail["name"]

        tree = parse_template_into_tree(template)
        elements = get_elements_for_open_data(tree)

        if len(elements["title"]) > 0:
            elements["title"][0].text = dataset["title"]

        if len(elements["date_revised"]) > 0:
            date_revised = elements["date_revised"][0]
            revised_tag = get_date_tag_from_code_tag(date_revised)
            revised_tag.text = dataset["modified"]

        if len(elements["date_published"]) > 0:
            date_published_code = elements["date_published"][0]
            published_tag = get_date_tag_from_code_tag(date_published_code)
            published_tag.text = dataset["issued"]

        if len(elements["title"]) > 0:
            elements["origin"][0].text = elements["publish"][0].text = dataset["publisher"]["name"]

        # bounding coordinates
        bbox = get_bbox(dataset)
        if bbox:
            elements["westbc"][0].text = bbox[0]
            elements["southbc"][0].text = bbox[1]
            elements["eastbc"][0].text = bbox[2]
            elements["northbc"][0].text = bbox[3]

        #TODO make more dynamic, eg clone CI_OnlineResource for each distribution option
        distribution_list = dataset["distribution"]
        for dist in distribution_list:
            if dist["format"] == "ZIP":
                elements["onlink"][0].text = dist["downloadURL"]
                elements["formname"][0].text = "shapefile"
            elif dist["format"] == "Esri REST":
                elements["onlink"][1].text = dist["accessUrl"]
                elements["formname"][1].text = "Esri REST Service"

        elements["datatype"][0].set("codeListValue", parse_datatype(dataset_detail))
        elements["id"][0].text = dataset["identifier"].split("/")[-1]
        elements["fileIdentifier"][0].text = dataset["identifier"]
        elements["accconst"][0].text = dataset["accessLevel"]

        # description oftentimes has HTML contents,
        # so use Beautiful Soup to get the plain text
        if dataset["description"]:
            abstract_soup = BeautifulSoup(dataset["description"])
            linebreaks = abstract_soup.findAll("br")
            [br.replace_with("&#xD;&#xA;") for br in linebreaks]
            elements["abstract"][0].text = abstract_soup.text
        else:
            elements["abstract"][0].text = "No description provided"

        elements["useconst"][0].text = dataset_detail["license"]

        keywords_list = dataset["keyword"]
        keywords_element = elements["themekey"][0].getparent().getparent()
        keyword_element = keywords_element.find("gmd:keyword",NSMAP)

        for index, keyword in enumerate(keywords_list):
            keywords_element.findall("gmd:keyword", NSMAP)[index].find("gco:CharacterString", NSMAP).text = keyword

            if index != len(keywords_list) - 1:
                keywords_element.append(deepcopy(keyword_element))

        timestamp = datetime.datetime.now().isoformat()
        elements["metadata_source"][0].text = elements["metadata_source"][0].text.format(url=dataset["identifier"],
            datetime=timestamp
        )
        elements["metadata_timestamp"][0].text = timestamp

        new_xml_filename = "{prefix}_{title}_{id}".format(prefix=prefix,
              title="".join(RE.findall(dataset["title"])).replace("__","_"),
              id=dataset["identifier"].split("/")[-1])

        #print os.path.join(output_path, new_xml_filename + ".xml")
        tree.write(os.path.join(output_path, new_xml_filename + ".xml"), pretty_print=True)


RE = re.compile('\w')

NSMAP = {
   "srv":"http://www.isotc211.org/2005/srv",
   "gco":"http://www.isotc211.org/2005/gco",
   "xlink":"http://www.w3.org/1999/xlink",
   "gts":"http://www.isotc211.org/2005/gts",
   "xsi":"http://www.w3.org/2001/XMLSchema-instance",
   "gml":"http://www.opengis.net/gml",
   "gmd":"http://www.isotc211.org/2005/gmd"
}

PATHS = {
    "title"    : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString",
    "onlink"   : "gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL",
    "formname" : "gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:name/gco:CharacterString",
    "origin"   : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString",
    "publish"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString",
    "date_published"       : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue='publication']",
    "date_revised"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue='revision']",
    "westbc"   : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:westBoundLongitude/gco:Decimal",
    "eastbc"   : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:eastBoundLongitude/gco:Decimal",
    "northbc"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:northBoundLatitude/gco:Decimal",
    "southbc"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:southBoundLatitude/gco:Decimal",
    "themekey" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode[@codeListValue='theme']",
    "placekey" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode[@codeListValue='place']",
    "abstract" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString",
    "accconst" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString",
    "useconst" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString",
    "id"       : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString",
    "datatype" : "gmd:spatialRepresentationInfo/gmd:MD_VectorSpatialRepresentation/gmd:geometricObjects/gmd:MD_GeometricObjects/gmd:geometricObjectType/gmd:MD_GeometricObjectTypeCode",
    "metadata_source": "gmd:metadataMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceNote/gco:CharacterString",
    "metadata_timestamp":"gmd:dateStamp/gco:DateTime",
    "fileIdentifier": "gmd:fileIdentifier"
}

FIELDS = PATHS.keys()

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
