#!/usr/bin/env sh

INFILE='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/lab/ObjectPackage_lab.xml'
STYLESHEET='/Users/todds/Otira/Projects/SAIT Test Bank Migration/d2l_migrator/stylesheets/assessments.xsl'
OUTDIR='/Users/todds/Otira/Projects/SAIT Test Bank Migration/output/lab'
BASEURL='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/lab'
# acceptible types include: all, cpd, mc, mr, msa, pe, sa, tf
QUESTIONTYPE='pe'
DIFFDIR=''

/Users/todds/Otira/Projects/SAIT\ Test\ Bank\ Migration/d2l_migrator/d2l_migrator/d2l_migrator.py -i "$INFILE" -s "$STYLESHEET" -o "$OUTDIR" -b "$BASEURL" -q "$QUESTIONTYPE" -d "$DIFFDIR"

`ctags -R --languages=python --exclude=.git -f ../d2l_migrator/tags --tag-relative=yes ../d2l_migrator/*`
