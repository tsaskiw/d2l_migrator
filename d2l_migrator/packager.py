from copy import deepcopy
import sys, os.path, zipfile, shutil, re
from lxml import etree
import transformer


MANIFEST_STYLESHEET_PATH = '../stylesheets/imsmanifest.xsl'


def package_assessments(etree, outdir_path):
    num_assessments = int(etree.xpath('count(//assessment)'))
    for index_of_assessment_to_package in range(1, num_assessments + 1):
        package_assessment(etree, index_of_assessment_to_package, outdir_path)


def package_assessment(etree, index_of_assessment_to_package, outdir_path):
    assessment_etree = build_assessment_etree(etree, index_of_assessment_to_package)
    assessment_ident = assessment_etree.getroot().getchildren()[0].get('ident')
    assessment_title = assessment_etree.getroot().getchildren()[0].get('title')
    temp_dir_path = make_temp_dir(assessment_ident, outdir_path)
    assessment_xml_doc_path = write_assessment_xml_doc(assessment_etree, temp_dir_path)
    manifest_file_path = write_manifest_file(assessment_ident, assessment_title, assessment_xml_doc_path, temp_dir_path)
    archive_path = os.path.join(outdir_path, assessment_title + '.zip')
    write_archive(assessment_xml_doc_path, manifest_file_path, archive_path)
    if zipfile.is_zipfile(archive_path):
        delete_temp_dir(temp_dir_path)
    else:
        print 'failed to archive assessment ' + assessment_ident + '. Please create manually'


def build_assessment_etree(etree, index_of_assessment_to_package):
    assessment_etree = deepcopy(etree)
    assessments_to_delete = assessment_etree.xpath('//assessment[not(position()=' + str(index_of_assessment_to_package) + ')]')
    if assessments_to_delete:
        for assessment_to_delete in assessments_to_delete:
            root = assessment_to_delete.getparent()
            if root is not None:
                root.remove(assessment_to_delete)
    return assessment_etree


def write_assessment_xml_doc(assessment_etree, outdir_path):
    assessment_ident = assessment_etree.getroot().getchildren()[0].get('ident')
    outfile_path = os.path.join(outdir_path, assessment_ident + '.xml')
    with open(outfile_path, 'w') as outfile:
        assessment_etree.write(outfile, pretty_print=True)
    return outfile_path


def make_temp_dir(name, outdir_path):
    temp_dir_path = os.path.join(outdir_path, name)
    os.mkdir(temp_dir_path)
    return temp_dir_path


def delete_temp_dir(temp_dir_path):
    shutil.rmtree(temp_dir_path)


def write_manifest_file(assessment_ident, assessment_title, assessment_xml_doc_path, temp_dir_path):
    file_name = os.path.split(assessment_xml_doc_path)[1]
    manifest_etree = build_manifest_etree(assessment_ident, assessment_title, file_name)
    result_etree = transformer.transform_data(manifest_etree, MANIFEST_STYLESHEET_PATH)
    manifest_file_path = os.path.join(temp_dir_path, 'imsmanifest.xml')
    with open(manifest_file_path, 'w') as manifest_file:
        result_etree.write(manifest_file, pretty_print=True)
    return manifest_file_path


def build_manifest_etree(assessment_ident, assessment_title, file_name):
    root = etree.Element('root')
    assessment_id_elt = etree.SubElement(root, 'assessment_id')
    file_name_elt = etree.SubElement(root, 'file_name')
    title_elt = etree.SubElement(root, 'title')
    assessment_id_elt.text = assessment_ident
    file_name_elt.text = file_name
    title_elt.text = assessment_title
    return root


def write_archive(assessment_xml_doc_path, manifest_file_path, archive_path):
    assessment_file_name = os.path.split(assessment_xml_doc_path)[1]
    manifest_file_name = os.path.split(manifest_file_path)[1]
    with zipfile.ZipFile(archive_path, mode='w') as archive:
        archive.write(assessment_xml_doc_path, assessment_file_name)
        archive.write(manifest_file_path, manifest_file_name)
