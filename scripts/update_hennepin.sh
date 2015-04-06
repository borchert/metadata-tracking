python scrape_open_data/__init__.py "http://gis.hennepin.opendata.arcgis.com/data.json" "henn" "../hennepin-county"
git add ../hennepin-county/*.xml
date_time=`date`
git commit -m "updated hennepin county dataset records: $date_time"