import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "OGP-metadata-py","src"))
import ogp2solr

s = ogp2solr.SolrOGP()
s.delete_query('Publisher:"Carver County"', no_confirm=True)
