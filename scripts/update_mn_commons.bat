@ECHO OFF
rem python update_mn_commons.py
python remove_BOM_folder.py ..\mn-geospatial-commons
python prettify_folder.py ..\mn-geospatial-commons