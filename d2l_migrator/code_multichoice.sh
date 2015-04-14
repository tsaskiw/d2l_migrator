#! /usr/bin/env sh
INFILE='/Users/todds/Otira/Projects/SAIT Test Bank Migration/tlm_exports/Period 1/Code/Period_1_-_Code_2014-Feb-16-2015/ObjectPackage.xml'
STYLESHEET='/Users/todds/Otira/Projects/SAIT Test Bank Migration/d2l_migrator/stylesheets/multichoice.xsl'
OUTFILE='/Users/todds/Otira/Projects/SAIT Test Bank Migration/output/code_mc.xml'
BASEURL='/Users/todds/Otira/Projects/SAIT Test Bank Migration/tlm_exports/Period 1/Code/Period_1_-_Code_2014-Feb-16-2015'

/Users/todds/Otira/Projects/SAIT\ Test\ Bank\ Migration/d2l_migrator/d2l_migrator/d2l_migrator.py -i "$INFILE" -s "$STYLESHEET" -o "$OUTFILE" -b "$BASEURL"

/usr/bin/xmllint --format -o "$OUTFILE" "$OUTFILE"
