import sys, re, os, os.path, shutil, zipfile
from lxml import etree

QUESTION = None
BASE_URL = None
IMAGE_OUTDIR_PATH = None
TEMP = None

def process_images(question, base_url, outdir):
    global QUESTION
    QUESTION = question
    global BASE_URL
    BASE_URL = base_url
    global IMAGE_OUTDIR_PATH
    IMAGE_OUTDIR_PATH = make_image_outdir(outdir)
    question_text_elt = get_question_text_elt(question)
    copy_image_files_and_replace_img_srcs(question_text_elt)

def make_image_outdir(outdir):
    image_outdir_path = os.path.join(outdir, 'images')
    if not os.path.isdir(image_outdir_path):
        os.makedirs(image_outdir_path)
    return image_outdir_path

def get_question_text_elt(question):
    global TEMP
    TEMP = question.findtext('Title')
    question_text_elts = question.xpath('Parts/QuestionPart/Text')
    if question_text_elts:
        question_text_elt = question_text_elts[0]
    return question_text_elt

def copy_image_files_and_replace_img_srcs(question_text_elt):
    question_text = question_text_elt.text
    src_pattern = '([\"\'])(.*getassetfile\.aspx\?id\s*=\s*)(\d+)([\"\'])'
    if re.search(src_pattern, question_text, re.IGNORECASE):
        new_question_text = re.sub(src_pattern, copy_image_file_and_replace_img_src, question_text, flags=re.IGNORECASE)
        question_text_elt.text = new_question_text

def copy_image_file_and_replace_img_src(image_text_match):
    new_image_text = image_text_match.group(0)
    image_id = image_text_match.group(3)
    image_file_name = copy_image_file(image_id)
    if image_file_name:
        new_image_text = image_text_match.group(1) + image_file_name + image_text_match.group(4)
    return new_image_text

def copy_image_file(image_id):
    image_file_name = get_image_file_name_by_asset_id(image_id)
    if image_file_name:
        archive_path = build_archive_path(image_id)
        if archive_contains_image_file(archive_path, image_file_name):
            with zipfile.ZipFile(archive_path, 'r') as image_archive:
                image_file_path = image_archive.extract(image_file_name, IMAGE_OUTDIR_PATH)
                new_image_file_path = rename_image_file(image_file_path, image_id)
        image_file_name = os.path.split(new_image_file_path)[1]
    return image_file_name

def get_image_file_name_by_asset_id(asset_id):
    image_file_name = None
    file_name_elts = QUESTION.xpath('//Asset[ID=' + asset_id + ']/FileName')
    if file_name_elts:
        image_file_name = file_name_elts[0].text
    return image_file_name

def build_archive_path(image_id):
    image_archive = image_id + '.zip'
    archive_path = os.path.join(BASE_URL, image_archive)
    return archive_path

def archive_contains_image_file(archive_path, image_file_name):
    contains_image_file = False
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, 'r') as image_archive:
            files = image_archive.namelist()
            contains_image_file = files.count(image_file_name) > 0
    return contains_image_file

def rename_image_file(image_file_path, image_id):
    image_dir_path, image_file_name = os.path.split(image_file_path)
    new_image_file_name = image_id + '_' + image_file_name
    new_image_file_path = os.path.join(image_dir_path, new_image_file_name)
    os.rename(image_file_path, new_image_file_path)
    return new_image_file_path
