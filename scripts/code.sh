#! /usr/bin/env sh
INFILE='/Users/todds/Otira/Projects/SAIT Test Bank Migration/tlm_exports/code/ObjectPackage.xml'
STYLESHEET='/Users/todds/Otira/Projects/SAIT Test Bank Migration/d2l_migrator/stylesheets/assessments.xsl'
OUTDIR='/Users/todds/Otira/Projects/SAIT Test Bank Migration/output/code'
BASEURL='/Users/todds/Otira/Projects/SAIT Test Bank Migration/tlm_exports/code'

/Users/todds/Otira/Projects/SAIT\ Test\ Bank\ Migration/d2l_migrator/d2l_migrator/d2l_migrator.py -i "$INFILE" -s "$STYLESHEET" -o "$OUTDIR" -b "$BASEURL"

`ctags -R --languages=python --exclude=.git .`
