@ECHO OFF
ECHO(
ECHO ------FGDC TESTS------
ECHO(
python ogp-mdt.py .\tests\fixtures\fgdc .\converted fgdc
ECHO(
ECHO ------MGMG TESTS------
ECHO(
python ogp-mdt.py .\tests\fixtures\mgmg .\converted mgmg
ECHO(
ECHO ------ISO TESTS-------
ECHO(
python ogp-mdt.py .\tests\fixtures\iso .\converted iso
ECHO(
ECHO ------SOLR TESTS------
ECHO(
python .\tests\test_solr.py
