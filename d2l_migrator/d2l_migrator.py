#! /usr/bin/env python

import sys, getopt, StringIO
from lxml import etree

def main(argv):
    collected_input = collect_input(argv)
    print(collected_input)
    if '' in collected_input:
        print_usage()
        sys.exit()

def collect_input(argv):
    infile = ''
    stylesheet = ''
    outfile = ''
    base_url = ''
    try:
        opts, args = getopt.getopt(argv,"hi:s:o:b:",["ifile=","sfile=","ofile=","base_url="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    if len(opts) == 0:
        print_usage()
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = arg
        elif opt in ("-s", "--sfile"):
            stylesheet = arg
        elif opt in ("-o", "--ofile"):
            outfile = arg
        elif opt in ("-b", "--base_url"):
            base_url = arg

    return (infile, stylesheet, outfile, base_url)

def print_usage():
    print('d2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputfile> -b <baseurl>')


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
