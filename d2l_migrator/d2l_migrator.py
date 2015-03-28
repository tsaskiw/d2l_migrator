#! /usr/bin/env python

import sys, getopt, StringIO
from lxml import etree

def main(argv):
    infile = ''
    stylesheet = ''
    outfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:s:o:",["ifile=","sfile=","ofile="])
    except getopt.GetoptError:
        print('d2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputfile>')
        sys.exit(2)
    if len(opts) == 0:
        print('d2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputfile>')
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print('d2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputfile')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = arg
        elif opt in ("-s", "--sfile"):
            stylesheet = arg
        elif opt in ("-o", "--ofile"):
            outfile = arg

    migrate_questions(infile, stylesheet, outfile)

def migrate_questions(infile, stylesheet, outfile):
    write_result(transform_data(load_source(infile), stylesheet), outfile)

def load_source(infile):
    dom = etree.parse(infile)
    return dom

def transform_data(dom, stylesheet):
    xslt = etree.parse(stylesheet)
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    return newdom

def write_result(dom, outfile_path):
    outfile = open(outfile_path, 'w')
    out = StringIO.StringIO()
    print(dom)
    #dom.write(outfile)
    #dom.write(out)
    outfile.close()
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
