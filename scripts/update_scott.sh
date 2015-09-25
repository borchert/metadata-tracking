python scrape_open_data/__init__.py "http://data.scottcounty.opendata.arcgis.com/data.json" "scott" "../scott-county"
../scott-county/ git iaddpw *.xml
date_time=`date`
git commit -m "updated scott county dataset records: $date_time"
