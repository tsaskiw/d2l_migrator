#! /usr/bin/env sh
<<<<<<< HEAD
=======

>>>>>>> develop
INFILE='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/math/ObjectPackage_math.xml'
STYLESHEET='/Users/todds/Otira/Projects/SAIT Test Bank Migration/d2l_migrator/stylesheets/assessments.xsl'
OUTDIR='/Users/todds/Otira/Projects/SAIT Test Bank Migration/output/math'
BASEURL='/Users/todds/Otira/Projects/SAIT Test Bank Migration/TLM/tlm_exports/math'
<<<<<<< HEAD
QUESTIONTYPE='msa'
=======
QUESTIONTYPE='mr'
DIFFDIR=''
>>>>>>> develop

/Users/todds/Otira/Projects/SAIT\ Test\ Bank\ Migration/d2l_migrator/d2l_migrator/d2l_migrator.py -i "$INFILE" -s "$STYLESHEET" -o "$OUTDIR" -b "$BASEURL" -q "$QUESTIONTYPE" -d "$DIFFDIR"

`ctags -R --languages=python --exclude=.git -f ../d2l_migrator/tags --tag-relative=yes ../d2l_migrator/*`
