#! /usr/bin/env python

import sys
import input_management
from lxml import etree

def main(argv):
    infile, stylesheet, outfile, base_url = input_management.get_input(argv)
    print(infile)

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
