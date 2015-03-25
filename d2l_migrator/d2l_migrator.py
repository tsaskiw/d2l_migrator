#! /usr/bin/env python

import sys, getopt
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
    #print('Questions migrated')

def load_source(infile):
    print('\nLoading datafile: ' + infile + '...')
    dom = etree.parse(infile)
    print('...done.')
    return dom

def transform_data(data, stylesheet):
    #print(''.join(['Stylesheet [', stylesheet, '] loaded']))
    #print('Data transformed')
    return 'transformed data'

def write_result(data, outfile):
    #print(data + ' written to ' + outfile)
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
