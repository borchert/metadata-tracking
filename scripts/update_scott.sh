rm ../scott-county/*.xml
python scrape_open_data/__init__.py "http://opendata.gis.co.scott.mn.us/data.json" "scott" "../scott-county" "scrape_open_data/scott_template_iso.xml"
#../scott-county/ git iaddpw *.xml
#date_time=`date`
#git commit -m "updated scott county dataset records: $date_time"
