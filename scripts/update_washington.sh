rm ../washington-county/*.xml
python scrape_open_data/__init__.py "http://data.wcmn.opendata.arcgis.com" "wash" "../washington-county" "scrape_open_data/washington_template_iso.xml"
