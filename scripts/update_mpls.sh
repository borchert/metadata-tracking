rm ../minneapolis/*.xml
python scrape_open_data/__init__.py "http://opendata.minneapolismn.gov/data.json" "mpls" "../minneapolis" "scrape_open_data/minneapolis_template_iso.xml"
#git iaddpw ../minneapolis/*.xml
#date_time=`date`
#git commit -m "updated minneapolis records: $date_time"
