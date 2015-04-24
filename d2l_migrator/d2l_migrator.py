#! /usr/bin/env python

import sys, os.path
from lxml import etree
import input_management, transformer, preprocessor, packager

def main(argv):
    infile_path, stylesheet_path, outdir_path, base_url = get_input(argv)
    preprocessed_dom = preprocessor.process(infile_path, base_url, outdir_path)
#    write_result(preprocessed_dom, 'pp_source.xml')
    transformed_etree = transformer.transform_data(preprocessed_dom, stylesheet_path)
#    write_result(transformed_etree, os.path.join(outdir_path, 'code.xml'))
    packager.package_assessments(transformed_etree, outdir_path)

def get_input(argv):
    infile_path, stylesheet_path, outdir_path, base_url = input_management.collect_input(argv)
    input_is_valid = input_management.validate_input(infile_path, stylesheet_path, outdir_path, base_url)
    if not input_is_valid:
        sys.exit()
    return (infile_path, stylesheet_path, outdir_path, base_url)

def write_result(dom, outfile_path):
    with open(outfile_path, 'w') as outfile:
        dom.write(outfile, pretty_print=True)

def print_usage(msg='Usage:'):
    print(msg)
    print('d2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputdir> -b <baseurl>')

if __name__ == "__main__":
    main(sys.argv[1:])
