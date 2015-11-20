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
            return element.find("gco:DateTime", NSMAP)


def guess_iso_topic_categories(keywords_list):
    categories_dict = {}
    final_categories = []
    for keyword in keywords_list:
        kw = keyword.lower()
        for topic in ISO_TOPIC_CATEGORIES:
            if kw in ISO_TOPIC_CATEGORIES[topic]:
                if categories_dict.has_key(topic):
                    categories_dict[topic] = categories_dict[topic] + 1
                else:
                    categories_dict[topic] = 1
    categories_list = categories_dict.items()
    if len(categories_list) == 0:
        return False
    sorted_categories = sorted(categories_list, key=itemgetter(1), reverse=True)
    top_category = sorted_categories[0]
    top_category_val = top_category[1]
    for i in sorted_categories:
        if i[1] == top_category_val:
            final_categories.append(i)
    return [i[0] for i in final_categories]


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
            temporal_extent = elements["temporal_extent"][0]
            revised_tag = get_date_tag_from_code_tag(date_revised)
            revised_tag.text = temporal_extent.text = dataset["modified"]

        if len(elements["date_published"]) > 0:
            date_published_code = elements["date_published"][0]
            published_tag = get_date_tag_from_code_tag(date_published_code)
            published_tag.text = dataset["issued"]

        if len(elements["title"]) > 0:
            #pdb.set_trace()
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
                elements["onlink"][1].text = dist["accessURL"]
                elements["formname"][1].text = "Esri REST Service"

        elements["datatype"][0].set("codeListValue", parse_datatype(dataset_detail))
        elements["id"][0].text = dataset["identifier"]
        elements["fileIdentifier"][0].text = dataset["identifier"]
        elements["accconst"][0].text = dataset["accessLevel"]

        if dataset_detail["record_count"]:
            elements["feature_count"][0].text = unicode((dataset_detail["record_count"]))

        # description oftentimes has HTML contents,
        # so use Beautiful Soup to get the plain text
        if dataset["description"]:
            abstract_soup = BeautifulSoup(dataset["description"])
            elements["abstract"][0].text = abstract_soup.text.strip().replace("\"","'").replace("&#160",". ")
        else:
            elements["abstract"][0].text = "No description provided"

        #rely on template version for this
        #elements["useconst"][0].text = dataset_detail["license"]

        keywords_list = dataset["keyword"]
        keywords_element = elements["themekey"][0].getparent().getparent()
        keyword_element = keywords_element.find("gmd:keyword", NSMAP)

        for index, keyword in enumerate(keywords_list):
            keywords_element.findall("gmd:keyword", NSMAP)[index].find("gco:CharacterString", NSMAP).text = keyword

            if index != len(keywords_list) - 1:
                keywords_element.append(deepcopy(keyword_element))

        topic_categories = guess_iso_topic_categories(keywords_list)
        if topic_categories:
            if len(topic_categories) == 1:
                elements["topic_categories"][0].find("gmd:MD_TopicCategoryCode", NSMAP).text = topic_categories[0]
            else:
                for topic in topic_categories:
                    parent = elements["topic_categories"][0].getparent()
                    index = parent.index(elements["topic_categories"][0])
                    copy = deepcopy(elements["topic_categories"][0])
                    copy.find("gmd:MD_TopicCategoryCode", NSMAP).text = topic
                    parent.insert(index, copy)
                all_topic_codes = parent.findall("gmd:topicCategory/gmd:MD_TopicCategoryCode",NSMAP)
                for i in all_topic_codes:
                    if i.text is None:
                        parent.remove(i.getparent())

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
    "origin"   : "gmd:contact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode[@codeListValue='originator']/../../gmd:organisationName/gco:CharacterString",
    "publish"   : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode[@codeListValue='publisher']/../../gmd:organisationName/gco:CharacterString",
    "date_published"       : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue='publication']",
    "date_revised"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue='revision']",
    "temporal_extent": "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimeInstant",
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
    "fileIdentifier": "gmd:fileIdentifier/gco:CharacterString",
    "feature_count": "gmd:spatialRepresentationInfo/gmd:MD_VectorSpatialRepresentation/gmd:geometricObjects/gmd:MD_GeometricObjects/gmd:geometricObjectCount/gco:Integer",
    "topic_categories": "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory"
}

ISO_TOPIC_CATEGORIES = {
    "farming" : "farming: rearing of animals or cultivation of plants. for example, resources describing irrigation, aquaculture, herding, and pests and diseases affecting crops and livestock.",
    "biota" : "biota: naturally occurring flora and fauna. for example, resources describing wildlife, biological sciences, ecology, wilderness, sea life, wetlands, and habitats.",
    "boundaries" : "boundaries: legal land descriptions.",
    "climatologyMeteorologyAtmosphere" : "climatology/meteorology/atmosphere: atmospheric processes and phenomena. for example, resources describing cloud cover, weather, atmospheric conditions, climate change, and precipitation.",
    "economy" : "economy: economic activities or employment. for example, resources describing labor, revenue, commerce, industry, tourism and ecotourism, forestry, fisheries, commercial or subsistence hunting, and exploration and exploitation of resources such as minerals, oil, and gas.",
    "elevation" : "elevation: height above or below sea level. for example, resources describing altitude, bathymetry, digital elevation models, slope, and products derived from this information.",
    "environment" : "environment: environmental resources, protection, and conservation. for example, resources describing pollution, waste storage and treatment, environmental impact assessment, environmental risk, and nature reserves.",
    "geoscientificinformation" : "geoscientific information: earth sciences. for example, resources describing geophysical features and processes, minerals, the composition, structure and origin of the earth’s rocks, earthquakes, volcanic activity, landslides, gravity information, soils, permafrost, hydrogeology, and erosion.",
    "health" : "health: health services,human ecology, and safety. for example, resources describing human disease and illness, factors affecting health, hygiene, mental and physical health, substance abuse, and health services.",
    "imageryBaseMapsEarthCover" : "imagery/base maps/earth cover: base maps. for example, resources describing land cover, topographic maps, and classified and unclassified images.",
    "intelligenceMilitary" : "intelligence/military: military bases, structures, and activities. for example, resources describing barracks, training grounds, military transportation, and information collection.",
    "inlandWaters" : "inland waters: inland water features, drainage systems, and their characteristics. for example, resources describing rivers and glaciers, salt lakes, water use plans, dams, currents, floods, water quality, and hydrographic charts.",
    "location" : "location: positional information and services. for example, resources describing addresses, geodetic networks, postal zones and services, control points, and place names.",
    "oceans" : "oceans: features and characteristics of salt water bodies excluding inland waters. for example, resources describing tides, tidal waves, coastal information, and reefs.",
    "planningCadastre" : "planning cadastre:land use. for example, resources describing zoning maps, cadastral surveys, and land ownership.",
    "society" : "society: characteristics of societies and cultures. for example, resources describing natural settlements, anthropology, archaeology, education, traditional beliefs, manners and customs, demographic data, crime and justice, recreational areas and activities, social impact assessments, and census information.",
    "structure" : "structure: man-made construction. for example, resources describing buildings, museums, churches, factories, housing, monuments, and towers.",
    "transportation" : "transportation: means and aids for conveying people and goods. for example, resources describing roads, airports and airstrips, shipping routes, tunnels, nautical charts, vehicle or vessel location, aeronautical charts, and railways.",
    "utilitiesCommunications" : "utilities/communications: energy, water and waste systems, and communications infrastructure and services. for example, resources describing hydroelectricity, geothermal, solar, and nuclear sources of energy, water purification and distribution, sewage collection and disposal, electricity and gas distribution, data communication, telecommunication, radio, and communication networks."
}


FIELDS = PATHS.keys()

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
