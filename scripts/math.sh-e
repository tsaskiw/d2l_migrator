#! /usr/bin/env sh
INFILE='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/math/ObjectPackage.xml'
STYLESHEET='/Users/todds/Otira/Projects/SAIT Test Bank Migration/d2l_migrator/stylesheets/assessments.xsl'
OUTDIR='/Users/todds/Otira/Projects/SAIT Test Bank Migration/output/math'
BASEURL='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/math'
QUESTIONTYPE='all'

/Users/todds/Otira/Projects/SAIT\ Test\ Bank\ Migration/d2l_migrator/d2l_migrator/d2l_migrator.py -i "$INFILE" -s "$STYLESHEET" -o "$OUTDIR" -b "$BASEURL" -q "$QUESTIONTYPE"

`ctags -R --languages=python --exclude=.git -f ../d2l_migrator/tags --tag-relative=yes ../d2l_migrator/*`
