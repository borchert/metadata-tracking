python scrape_open_data/__init__.py "http://openramsey.ramseygis.opendata.arcgis.com/data.json" "rams" "../ramsey-county-eod"
sed -i '' 's/FeatureServer/MapServer/g' ../ramsey-county-eod/*
git iaddpw
