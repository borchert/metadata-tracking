import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "OGP-metadata-py","src"))
import ogp2solr

s = ogp2solr.SolrOGP()

s.delete_query('Publisher:"Dakota County"', no_confirm=True)
s.delete_query('Publisher:"Lake County"', no_confirm=True)
s.delete_query('Publisher:"Metro GIS"', no_confirm=True)
s.delete_query('Publisher:"Metropolitan Council"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Board of Water and Soil Resources (BWSR)"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Department of Agriculture"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Department of Education"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Department of Health', no_confirm=True)
s.delete_query('Publisher:"Minnesota Department of Natural Resources"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Department of Revenue"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Department of Transportation"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Geological Survey"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Geospatial Information Office"', no_confirm=True)
s.delete_query('Publisher:"Minnesota Pollution Control Agency"', no_confirm=True)
s.delete_query('Publisher:"University of Minnesota, Twin Cities"', no_confirm=True)
