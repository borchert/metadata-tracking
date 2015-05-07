"""
Script for writing ISO 19139 metadata for Esri Open Data datasets. Work in progress...
"""

from lxml import etree
import requests
from bs4 import BeautifulSoup
from copy import deepcopy
import os, os.path
import json

def check_for_local_data_json(PREFIX):
    if os.path.exists(PREFIX + "_data.json"):
        return True
    else:
        return False

def request_data_json(url, PREFIX):
    with open(PREFIX + "_data.json", "wb") as fp:
        print "remote request for data.json"
        try:
            j = requests.get(url).json()
        except requests.exceptions.HTTPError as e:
            sys.exit(e.message)
        else:
            fp.write(json.dumps(j))
            return j["dataset"]

def get_data_json(PREFIX,url):
    if not check_for_local_data_json(PREFIX):
        return request_data_json(url, PREFIX)
    else:
        return json.load(open(PREFIX + "_data.json"))["dataset"]

def get_elements_for_open_data(tree):
    field_map = {}
    for field in FIELDS:
        field_map[field] = tree.findall(PATHS[field],NSMAP)
    return field_map

def parse_template_into_tree(template_name="scrape_open_data/opendata_iso_template_gmd_gone.xml"):
    return etree.parse(template_name)

def get_bbox(dataset):
    return dataset["spatial"].split(",")

def check_for_landing_page_json(dataset):
    if landing_page_json is not None:
        return True
    else:
        return False

def get_landing_page_json(dataset):
    if not check_for_landing_page_json(dataset):
        try:
            r = requests.get(dataset["landingPage"]+".json")
        except requests.exceptions.HTTPError as e:
            sys.exit(e.message)
        finally:
            if "json" in r.headers["content-type"]:
                landing_page_json = r.json()
                return landing_page_json
            return None

def clear_landing_page_json():
    landing_page_json = None

def get_fields(dataset):
    #dataset_details = get_landing_page_json(dataset)
    #load local for now
    dataset_details = json.load(open("dataset_detail.json"))


def parse_webservice(dataset):
    url = dataset["webService"]

    #If it's a feature service, we don't want it (for now)
    if url.find("FeatureServer") is not -1:
        url = ""

    return url

def parse_datatype(dataset):

    try:
        geometryType = get_landing_page_json(dataset)["data"]["geometry_type"]
        print "geometryType: ", geometryType
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


def main(url, prefix, output_path):

    PREFIX = prefix
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    datasets = get_data_json(PREFIX, url)

    for dataset in datasets:
        print "Now on:", dataset["title"]
        tree = parse_template_into_tree()
        elements = get_elements_for_open_data(tree)

        if len(elements["title"]) > 0:
            elements["title"][0].text = dataset["title"]

        if len(elements["pubdate"]) > 0:
            elements["pubdate"][0].text = dataset["issued"]

        if len(elements["title"]) > 0:
            elements["origin"][0].text = elements["publish"][0].text = dataset["contactPoint"]["fn"]

        # bounding coordinates
        bbox = get_bbox(dataset)
        elements["westbc"][0].text = bbox[0]
        elements["southbc"][0].text = bbox[1]
        elements["eastbc"][0].text = bbox[2]
        elements["northbc"][0].text = bbox[3]

        distribution_list = dataset["distribution"]
        for dist in distribution_list:
            if dist["title"] == "Shapefile":
                elements["onlink"][0].text = dist["downloadURL"]
                elements["formname"][0].text = "shapefile"


        # REST service link
        elements["onlink"][1].text = parse_webservice(dataset)

        elements["datatype"][0].set("codeListValue", parse_datatype(dataset))


        elements["id"][0].text = dataset["identifier"]
        elements["accconst"][0].text = dataset["accessLevel"]

        # description and license oftentimes have HTML contents,
        # so use Beautiful Soup to get the plain text



        if dataset["description"]:
            abstract_soup = BeautifulSoup(dataset["description"])
            #elements["abstract"][0].text = u' \n'.join(abstract_soup.findAll(text=True))
            elements["abstract"][0].text = dataset["description"]
        else:
            elements["abstract"][0].text = "No description provided"

        elements["useconst"][0].text = dataset["license"]



        keywords_list = dataset["keyword"]

        keywords_element = elements["themekey"][0].getparent().getparent()
        keyword_element = keywords_element.find("gmd:keyword",NSMAP)

        for index, keyword in enumerate(keywords_list):
            keywords_element.findall("gmd:keyword", NSMAP)[index].find("gco:CharacterString", NSMAP).text = keyword

            if index != len(keywords_list) - 1:
                keywords_element.append(deepcopy(keyword_element))

        elements["placekey"][0].getparent().getparent().find("gmd:keyword/gco:CharacterString", NSMAP).text = "Hennepin County (Minn.)"

        new_xml_filename = "{prefix}_{title}_{id}".format(prefix=PREFIX,
                                                          title=dataset["title"].replace(" ", "_").lower(),
                                                          id=dataset["identifier"].split("/")[-1])

        print os.path.join(output_path, new_xml_filename + ".xml")
        tree.write(os.path.join(output_path, new_xml_filename + ".xml"), pretty_print=True)


NSMAP = {
   "srv":"http://www.isotc211.org/2005/srv",
   "gco":"http://www.isotc211.org/2005/gco",
   "xlink":"http://www.w3.org/1999/xlink",
   "gts":"http://www.isotc211.org/2005/gts",
   "xsi":"http://www.w3.org/2001/XMLSchema-instance",
   "gml":"http://www.opengis.net/gml",
   "gmd":"http://www.isotc211.org/2005/gmd"
}

FIELDS = [
    "title",
    "pubdate" ,
    "onlink"  ,
    "origin"  ,
    "publish" ,
    "westbc"  ,
    "eastbc"  ,
    "northbc" ,
    "southbc" ,
    "themekey",
    "placekey",
    "abstract",
    "accconst",
    "useconst",
    "formname",
    "id",
    "datatype"
]

PATHS = {
    "title"    : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString",
    "onlink"   : "gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL",
    "origin"   : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString",
    "publish"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString",
        "pubdate"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:editionDate/gco:Date",
"westbc"   : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:westBoundLongitude/gco:Decimal",
    "eastbc"   : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:eastBoundLongitude/gco:Decimal",
    "northbc"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:northBoundLatitude/gco:Decimal",
    "southbc"  : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/gmd:southBoundLatitude/gco:Decimal",
    "themekey" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode[@codeListValue='theme']",
    "placekey" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode[@codeListValue='place']",
    "abstract" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString",
    "accconst" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString",
    "useconst" : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString",
    "formname" : "gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString",
    "id"       : "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString",
    "datatype" : "gmd:spatialRepresentationInfo/gmd:MD_VectorSpatialRepresentation/gmd:geometricObjects/gmd:MD_GeometricObjects/gmd:geometricObjectType/gmd:MD_GeometricObjectTypeCode"
}

landing_page_json = None

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2], sys.argv[3])




