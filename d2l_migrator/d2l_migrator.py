#!/usr/bin/env python

import logging, os.path, sys
from lxml import etree
import input_management, packager, preprocessor, transformer


WRITE_INTERMEDIATE_FILES = True
USAGE_MESSAGE = 'd2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputdir> -b <baseurl> -q <questiontype>=all [cpd, mc, mr, msa, sa, tf], <diffdir>=""'


def main(argv):
    infile_path, stylesheet_path, outdir_path, base_url, question_type, diffdir = get_input(argv)
    logging.basicConfig(filename=os.path.join(outdir_path, 'migrator.log'), level=logging.INFO, filemode='w')
    preprocessed_dom = preprocessor.process(infile_path, base_url, outdir_path, question_type, diffdir)
    if (WRITE_INTERMEDIATE_FILES):
        write_outfile(preprocessed_dom, 'pp_source.xml')
    transformed_etree = transformer.transform_data(preprocessed_dom, stylesheet_path)
    remove_empty_assessments(transformed_etree)
    if (WRITE_INTERMEDIATE_FILES):
        write_outfile(transformed_etree, os.path.join(outdir_path, 'out.xml'))
    packager.package_assessments(transformed_etree, outdir_path)


def remove_empty_assessments(transformed_etree):
    assessments_to_delete = transformed_etree.xpath('//assessment[not(section/item)]')
    if assessments_to_delete:
        for assessment_to_delete in assessments_to_delete:
            root = assessment_to_delete.getparent()
            if root is not None:
                root.remove(assessment_to_delete)


def get_input(argv):
    infile_path, stylesheet_path, outdir_path, base_url, question_type, diffdir = input_management.collect_input(argv)
    input_is_valid = input_management.validate_input(infile_path, stylesheet_path, outdir_path, base_url, question_type, diffdir)
    if not input_is_valid:
        sys.exit()
    return (infile_path, stylesheet_path, outdir_path, base_url, question_type, diffdir)


def write_outfile(dom, outfile_path):
    with open(outfile_path, 'w') as outfile:
        dom.write(outfile, pretty_print=True)


def print_usage(msg='Usage:'):
    print(msg)
    print(USAGE_MESSAGE)


if __name__ == "__main__":
    main(sys.argv[1:])
