#! /usr/bin/env python

import sys, StringIO
from lxml import etree
import input_management, transformer

def main(argv):
    infile, stylesheet, outfile, base_url = get_input(argv)
    result_etree = transform_questions(infile, stylesheet, base_url)
    write_result(result_etree, outfile)

def get_input(argv):
    infile, stylesheet, outfile, base_url = input_management.collect_input(argv)
    input_is_valid = input_management.validate_input(infile, stylesheet, base_url)
    if not input_is_valid:
        sys.exit()
    return (infile, stylesheet, outfile, base_url)

def transform_questions(infile, stylesheet, base_url):
    result_etree = transformer.transform_data(infile, stylesheet)
    #resource_paths = transformer.build_resource_paths(result_etree, base_url)
    return result_etree

def write_result(dom, outfile_path):
    outfile = open(outfile_path, 'w')
    dom.write(outfile)
    outfile.close()

def print_usage(msg='Usage:'):
    print(msg)
    print('d2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputfile> -b <baseurl>')

if __name__ == "__main__":
    main(sys.argv[1:])
