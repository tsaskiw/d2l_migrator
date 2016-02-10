#!/usr/bin/env sh

INFILE='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/Period 2/aelp_252_blended/ObjectPackage_aelp_252.xml'
STYLESHEET='/Users/todds/Otira/Projects/SAIT Test Bank Migration/d2l_migrator/stylesheets/assessments.xsl'
OUTDIR='/Users/todds/Otira/Projects/SAIT Test Bank Migration/output/Period 2/aelp_252'
BASEURL='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/Period 2/aelp_252_blended/'
# acceptible types include: all, cpd, mc, mr, msa, pe, sa, tf
QUESTIONTYPE='all'
DIFFDIR=''
QUESTION_LIST_FILE=''

/Users/todds/Otira/Projects/SAIT\ Test\ Bank\ Migration/d2l_migrator/d2l_migrator/d2l_migrator.py -i "$INFILE" -s "$STYLESHEET" -o "$OUTDIR" -b "$BASEURL" -q "$QUESTIONTYPE" -d "$DIFFDIR" -l "$QUESTION_LIST_FILE"

`ctags -R --languages=python --exclude=.git -f ../../d2l_migrator/tags --tag-relative=yes ../../d2l_migrator/*`
