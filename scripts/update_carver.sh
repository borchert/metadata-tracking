python scrape_open_data/__init__.py "http://data.carver.opendata.arcgis.com/data.json" "carver" "../carver-county"
git add ../carver-county/*.xml
date_time=`date`
git commit -m "updated carver county dataset records: $date_time"
