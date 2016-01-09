import fnmatch, logging, os, sys
import csv
import random
import re
from types import *
from lxml import etree
from html import HTML
import image_processor
import p2_unicode_utils


COUNT_ONLY = False

Q_TYPE_ALL = 'ALL'
Q_TYPE_COMPOUND = 'COMPOUND'
Q_TYPE_CUSTOM = 'CUSTOM'
Q_TYPE_MULTICHOICE = 'MULTICHOICE'
Q_TYPE_MULTIRESPONSE = 'MULTIRESPONSE'
Q_TYPE_MULTISHORTANSWER = 'MULTISHORTANSWER'
Q_TYPE_PARSEREXPRESSION = 'PARSEREXPRESSION'
Q_TYPE_SHORTANSWER = 'SHORTANSWER'
Q_TYPE_TRUEFALSE = 'TRUEFALSE'
Q_TYPE_UNKNOWN = 'UNKNOWN'

Q_TYPE_NUMBER = 'q_type_number'
Q_TYPE_SYMBOL = 'q_type_symbol'

Q_TYPES = {
    Q_TYPE_ALL: {Q_TYPE_NUMBER: '', Q_TYPE_SYMBOL: 'all'},
    Q_TYPE_COMPOUND: {Q_TYPE_NUMBER: '6.2', Q_TYPE_SYMBOL: 'cpd'},
    Q_TYPE_CUSTOM: {Q_TYPE_NUMBER: '6', Q_TYPE_SYMBOL: 'cs'},
    Q_TYPE_MULTICHOICE: {Q_TYPE_NUMBER: '1', Q_TYPE_SYMBOL: 'mc'},
    Q_TYPE_MULTIRESPONSE: {Q_TYPE_NUMBER: '2', Q_TYPE_SYMBOL: 'mr'},
    Q_TYPE_MULTISHORTANSWER: {Q_TYPE_NUMBER: '6.1', Q_TYPE_SYMBOL: 'msa'},
    Q_TYPE_PARSEREXPRESSION: {Q_TYPE_NUMBER: '6.3', Q_TYPE_SYMBOL: 'pe'},
    Q_TYPE_SHORTANSWER: {Q_TYPE_NUMBER: '3', Q_TYPE_SYMBOL: 'sa'},
    Q_TYPE_TRUEFALSE: {Q_TYPE_NUMBER: '4', Q_TYPE_SYMBOL: 'mc'},
    Q_TYPE_UNKNOWN: {Q_TYPE_NUMBER: '0', Q_TYPE_SYMBOL: 'unk'}}

LC_TRUE_VALUES = ['t', 'true', 'y']
LC_FALSE_VALUES = ['f', 'false', 'n']

RE_PATTERN_VARIABLE = r'\b([a-zA-Z]+[\d_]*[\w\d]*)'
VARIABLE_REPLACEMENT_E = 'e_e'


def process(infile_path, base_url, outdir, question_type_symbol, diffdir, question_list_file):
    source_etree = parse_question_source_file(infile_path)
    set_up_logging(source_etree, infile_path)
    collect_unassigned_questions(source_etree)
    set_custom_question_subtypes(source_etree)
    remove_duplicate_questions_from_source(source_etree, diffdir)
    remove_assessments_without_question_type(question_type_symbol, source_etree)
    remove_questions_other_than(question_type_symbol, source_etree)
    result_etree = process_questions(source_etree, base_url, outdir, question_list_file)
    return result_etree


def parse_question_source_file(infile_path):
    parser = etree.XMLParser(remove_blank_text=True)
    source_etree = etree.parse(infile_path, parser)
    return source_etree


def set_up_logging(source_etree, infile_path):
    logging.info("Loading file '{}'".format(infile_path))


def collect_unassigned_questions(source_etree):
    unassigned_questions = get_unassigned_questions(source_etree)
    assessments = build_module_assessments(unassigned_questions)
    add_module_assessments(assessments, source_etree)


def get_unassigned_questions(source_etree):
    questions = source_etree.xpath('//Question[not(ancestor::Assessment)]')
    assessment_question_titles = source_etree.xpath('//Question[ancestor::Assessment]/Title/text()')
    non_assessment_questions = [question for question in questions if question.findtext('Title') not in assessment_question_titles]
    return non_assessment_questions


def build_module_assessments(unassigned_questions):
    assessments = {}
    for question in unassigned_questions:
        module_assessment = get_module_assessment(question, assessments)
        add_question_to_module_assessment(question, module_assessment)
    return assessments.values()


def add_module_assessments(assessments, source_etree):
    for assessment in assessments:
        print(assessment.findtext('Title'))
        source_etree.getroot().append(assessment)


def get_module_assessment(question, assessments):
    assessment_title = get_module_assessment_title(question)
    if assessment_title not in assessments:
        assessments[assessment_title] = build_module_assessment(assessment_title)
    return assessments[assessment_title]


def get_module_assessment_title(question):
    title = question.xpath('following-sibling::ContentModule/Title/text()')[0]
    if not title.endswith('2015'):
        title = ''.join([title, '-2015'])
    title = re.sub(r'[/\\:]', r'-', title)
    return title


def build_module_assessment(assessment_title):
    assessment_node = etree.Element('Assessment')
    assessment_node.append(get_module_assessment_title_node(assessment_title))
    assessment_node.append(get_id_node())
    assessment_node.append(get_selections_node())
    return assessment_node


def get_module_assessment_title_node(assessment_title):
    title_node = create_node('Title')
    title_node.text = assessment_title
    return title_node


def get_id_node():
    id_node = create_node('ID')
    id_node.text = str(random.randint(1, 99999)).zfill(5)
    return id_node


def get_selections_node():
    selections_node = create_node('Selections')
    selections_node.append(get_assessment_selection_node())
    return selections_node


def get_assessment_selection_node():
    assessment_selection_node = create_node('AssessmentSelection')
    assessment_selection_node.append(get_content_selection_sets_node())
    return assessment_selection_node


def get_content_selection_sets_node():
    return create_node('ContentSelectionSets')


def create_node(title):
    return etree.Element(title)


def create_assessment(content_module_title):
    title = etree.Element('Title')
    title.text = content_module_title
    identifier = etree.Element('ID')
    identifier.text = str(random.randint(0,99999)).zfill(5)
    assessment = etree.Element('Assessment')
    assessment.append(title)
    assessment.append(identifier)
    return assessment

def add_question_to_module_assessment(question, module_assessment):
    content_selection_sets = module_assessment.xpath('Selections/AssessmentSelection/ContentSelectionSets')[0]
    content_selection_sets.append(question)


def add_question_to_assessment(na_question, assessment):
    node_names = ['ContentSelectionSets', 'AssessmentSelection', 'Selections']
    nodes = [etree.Element(name) for name in node_names]
    nodes.append(na_question)
    nodes.insert(0, assessment)
    iterator = iter(nodes)
    prev = iterator.next()
    for node in iterator:
        prev.append(node)
        prev = node


def set_custom_question_subtypes(source_etree):
    custom_questions = get_custom_questions(source_etree)
    for custom_question in custom_questions:
        subtype_number = find_subtype_number_for_custom_question(custom_question)
        set_question_type(custom_question, subtype_number)


def get_custom_questions(source_etree):
    custom_type_number = get_question_type_number_as_string_for_name(Q_TYPE_CUSTOM)
    custom_questions = source_etree.xpath('/TLMPackage/Assessment/Selections/AssessmentSelection/ContentSelectionSets/Question[Type=' + custom_type_number + ']')
    return custom_questions


def find_subtype_number_for_custom_question(custom_question):
    if is_parser_expression_question(custom_question):
        subtype_number = get_question_type_number_as_string_for_name(Q_TYPE_PARSEREXPRESSION)
    elif is_single_part_question(custom_question):
        subtype_number = get_type_number_for_custom_single_part_question(custom_question)
    elif is_multiple_short_answer_question(custom_question):
        subtype_number = get_question_type_number_as_string_for_name(Q_TYPE_MULTISHORTANSWER)
    elif is_compound_question(custom_question):
        subtype_number = get_question_type_number_as_string_for_name(Q_TYPE_COMPOUND)
    else:
        subtype_number = get_question_type_number_as_string_for_name(Q_TYPE_UNKNOWN)
    return subtype_number


def set_question_type(custom_question, subtype_number):
    question_type = custom_question.find('Type')
    question_type.text = subtype_number


def is_multiple_short_answer_question(question):
    is_msa = doesnt_contain_parser_expression(question) and contains_multiple_short_answer_parts(question) and contains_single_part_type(question)
    return is_msa


def is_single_part_question(question):
    return question.xpath('count(Parts/QuestionPart)') == 1


def get_type_number_for_custom_single_part_question(question):
    type_number = question.find('Parts').find('QuestionPart').findtext('Type')
    return type_number


def is_compound_question(question):
    is_compound = doesnt_contain_parser_expression(question) and isnt_msa_question(question) and contains_multiple_question_parts(question)
    return is_compound


def isnt_msa_question(question):
    return not is_multiple_short_answer_question(question)


def is_parser_expression_question(question):
    return contains_parser_expression(question)


def contains_multiple_short_answer_parts(question):
    short_answer_type_number = get_question_type_number_as_string_for_name(Q_TYPE_SHORTANSWER)
    short_answer_parts = question.xpath('Parts/QuestionPart[Type=' + short_answer_type_number + ']')
    return len(short_answer_parts) > 1


def contains_multiple_question_parts(question):
    question_part_count = question.xpath('count(Parts/QuestionPart)')
    return question_part_count > 1


def contains_multiple_part_types(question):
    question_part_types = question.xpath('Parts/QuestionPart/Type/text()')
    unique_question_part_types = list(set(question_part_types))
    return len(unique_question_part_types) > 1


def contains_single_part_type(question):
    return not contains_multiple_part_types(question)


def contains_parser_expression(question):
    return question.findtext('ParserExpression')


def doesnt_contain_parser_expression(question):
    return not contains_parser_expression(question)


def remove_duplicate_questions_from_source(source_etree, diffdir=''):
    if diffdir:
        existing_question_titles = find_existing_question_titles(diffdir)
        remove_duplicate_questions_from_module(source_etree, existing_question_titles)
        remove_empty_assessments_from_modules(source_etree)


def find_existing_question_titles(diffdir):
    existing_question_titles = set()
    existing_file_paths = get_existing_file_paths(diffdir)
    for existing_file_path in existing_file_paths:
        parser = etree.XMLParser(remove_blank_text=True)
        source_etree = etree.parse(existing_file_path, parser)
        existing_question_titles = existing_question_titles.union(set(source_etree.xpath('/*/assessment/section/item/@title')))
    return existing_question_titles


def get_existing_file_paths(diffdir):
    existing_files = []
    for filename in os.listdir(diffdir):
        if fnmatch.fnmatch(filename, 'quiz_d2l_*.xml'):
            filepath = os.path.join(diffdir, filename)
            if os.path.isfile(filepath):
                existing_files.append(filepath)
    return existing_files


def remove_duplicate_questions_from_module(module_etree, existing_question_titles):
    for question in module_etree.iter('Question'):
        if question.findtext('Title') in existing_question_titles:
            parent = question.getparent()
            parent.remove(question)


def remove_empty_assessments_from_modules(source_etree):
    for assessment in source_etree.iter('Assessment'):
        if assessment.find('.//Question') is None:
            parent = assessment.getparent()
            parent.remove(assessment)


def remove_assessments_without_question_type(question_type_symbol, source_etree):
    question_type = get_question_type_name_for_symbol(question_type_symbol)
    if question_type != Q_TYPE_ALL:
        assessments = source_etree.findall('//Assessment')
        question_type_number = get_question_type_number_as_string_for_name(question_type)
        for assessment in assessments:
            questions = assessment.xpath('descendant::Question[Type=' + question_type_number + ']')
            if not questions:
                assessment.getparent().remove(assessment)
            else:
                logging.info(''.join([assessment.findtext('Title'), ' : ', str(len(questions))]))


def remove_questions_other_than(question_type_symbol, source_etree):
    question_type = get_question_type_name_for_symbol(question_type_symbol)
    if question_type != Q_TYPE_ALL:
        question_type_number = get_question_type_number_as_string_for_name(question_type)
        assessments = source_etree.findall('//Assessment')
        for assessment in assessments:
            questions = assessment.xpath('descendant::Question[Type!=' + question_type_number + ']')
            for question in questions:
                question.getparent().remove(question)


def process_questions(intree, base_url, outdir, question_list_file):
    cpd_question_count = 0
    mc_question_count = 0
    mr_question_count = 0
    msa_question_count = 0
    pe_question_count = 0
    pe_incompat_question_count = 0
    sa_question_count = 0
    tf_question_count = 0
    unk_question_count = 0
    d2l_incompatible_questions = {}

    question_list = build_question_list(question_list_file)
    types_string = get_question_types_string()
    query = "//Question[ancestor::Assessment and ({})]".format(types_string)
    questions = intree.xpath(query)
    log_input_questions(intree, questions)
    for question in questions:
        if is_required_question(question, question_list):
            question_type = get_question_type_name_for_number(question.findtext('Type'))
            if question_type == Q_TYPE_MULTISHORTANSWER:
                if not COUNT_ONLY:
                    process_msa_question(question)
                msa_question_count += 1
            elif question_type == Q_TYPE_MULTICHOICE:
                if not COUNT_ONLY:
                    process_mc_question(question)
                mc_question_count += 1
            elif question_type == Q_TYPE_MULTIRESPONSE:
                if not COUNT_ONLY:
                    process_mr_question(question)
                mr_question_count += 1
            elif question_type == Q_TYPE_SHORTANSWER:
                if not COUNT_ONLY:
                    process_sa_question(question)
                sa_question_count += 1
            elif question_type == Q_TYPE_TRUEFALSE:
                if not COUNT_ONLY:
                    process_tf_question(question)
                tf_question_count += 1
            elif question_type == Q_TYPE_COMPOUND:
                if not COUNT_ONLY:
                    process_cpd_question(question)
                cpd_question_count += 1
            elif question_type == Q_TYPE_PARSEREXPRESSION:
                if not COUNT_ONLY:
                    if is_d2l_compatible_pe_question(question):
                        process_pe_question(question)
                        pe_question_count += 1
                    else:
                        add_incompatible_question(question, d2l_incompatible_questions)
                        question.getparent().remove(question)
                        pe_incompat_question_count += 1
            else:
                unk_question_count += 1
                log_unrecognized_question(question)
            image_processor.process_images(question, base_url, outdir)
        else:
            question.getparent().remove(question)
    log_converted_questions(cpd_question_count, mc_question_count, mr_question_count, msa_question_count, pe_question_count, pe_incompat_question_count, sa_question_count, tf_question_count, unk_question_count)
    log_incompatible_questions(d2l_incompatible_questions, outdir)
    write_it()
    return intree


def build_question_list(question_list_file):
    """ takes path to an excel csv file, single column of question titles, builds a list"""
    question_list = []
    if os.path.isfile(question_list_file):
        with open(question_list_file, 'rbU') as ql_file:
            reader = csv.reader(ql_file)
            for row in reader:
                if len(row) >= 1:
                    question_list.append(row[0])
    return question_list


def is_required_question(question, question_list):
    is_required = True
    if len(question_list) > 0:
        title = question.findtext('Title')
        is_required = title in question_list
    return is_required


def log_input_questions(intree, questions):
    logging.info('INPUT')
    course_code = intree.findtext('ECourse/Code')
    logging.info("Course code: {}".format(course_code))
    logging.info("\tTotal questions input >>> {}".format(len(questions)))


def add_incompatible_question(question, d2l_incompatible_questions):
    assessment_name = question.xpath('ancestor::Assessment/Title/text()')[0]
    question_name = question.findtext('Title')
    if assessment_name in d2l_incompatible_questions:
        d2l_incompatible_questions[assessment_name].append(question_name)
    else:
        d2l_incompatible_questions[assessment_name] = [question_name]


def log_unrecognized_question(question):
    logging.info("Failed to recognize custom question type:")
    logging.info("Question: {}".format(question.findtext('Title')))
    logging.info("Type: {}".format(question.findtext('Type')))


def log_converted_questions(cpd_question_count, mc_question_count, mr_question_count, msa_question_count, pe_question_count, pe_incompat_question_count, sa_question_count, tf_question_count, unk_question_count):
    logging.info('OUTPUT')
    logging.info("Converted:")
    logging.info('cpd = ' + str(cpd_question_count))
    logging.info('mc = ' + str(mc_question_count))
    logging.info('mr = ' + str(mr_question_count))
    logging.info('msa = ' + str(msa_question_count))
    logging.info('pe = ' + str(pe_question_count))
    logging.info('sa = ' + str(sa_question_count))
    logging.info('tf = ' + str(tf_question_count))
    total_question_count = cpd_question_count + mc_question_count + mr_question_count + msa_question_count + pe_question_count + sa_question_count + tf_question_count
    logging.info('total = ' + str(total_question_count))
    logging.info("Not Converted:")
    logging.info("pe: " + str(pe_incompat_question_count))
    logging.info("unk: " + str(unk_question_count))
    logging.info("\tTotal questions processed >>> {}".format(total_question_count + pe_incompat_question_count + unk_question_count))


def log_incompatible_questions(incompatible_questions, outdir):
    file_path = os.path.join(outdir, 'd2l_incompatible_questions.txt')
    with open(file_path, 'w+', ) as logfile:
        for assessment in incompatible_questions:
            logfile.write("{}\n".format(p2_unicode_utils.to_str(assessment)))
            for question in incompatible_questions[assessment]:
                logfile.write("\t{}\n".format(question))


def get_question_type_name_for_number(question_type_number_as_string):
    return get_question_type_name_for_property(Q_TYPE_NUMBER, question_type_number_as_string)


def get_question_type_name_for_symbol(question_type_symbol):
    return get_question_type_name_for_property(Q_TYPE_SYMBOL, question_type_symbol)


def get_question_type_name_for_property(property_type, property_value):
    q_type_name = ''
    for q_type in Q_TYPES.items():
        if(q_type[1][property_type] == property_value):
            q_type_name = q_type[0]
    return q_type_name


def get_question_type_number_as_string_for_name(question_type_name):
    if question_type_name in Q_TYPES:
        return Q_TYPES[question_type_name][Q_TYPE_NUMBER]
    else:
        msg = "Question Type Number not found for name '{0}'".format(question_type_name)
        logging.error(msg)
        sys.exit()


def get_question_types_string():
    types_string = ' or '.join("Type={!s}".format(question_type[1][Q_TYPE_NUMBER]) for question_type in Q_TYPES.items())
    q_types_or_string = ''
    for question_type in Q_TYPES.items():
        q_type_number_as_string = question_type[1][Q_TYPE_NUMBER]
        if is_float(q_type_number_as_string):
            if len(q_types_or_string) > 0:
                q_types_or_string += ' or '
            q_types_or_string += 'Type='
            q_types_or_string += q_type_number_as_string
    return q_types_or_string


def process_mc_question(question):
    pp_answers = etree.Element('pp_answers')
    for question_choice in question.xpath('Parts/QuestionPart/Choices/QuestionChoice'):
        pp_answer = process_mc_answer(question, question_choice)
        pp_answers.append(pp_answer)
    question.insert(0, pp_answers)


def process_mc_answer(question, question_choice):
    pp_answer = etree.Element('pp_answer')
    pp_answer = add_answer_elt(question_choice, pp_answer, 'Number', 'number')
    pp_answer = add_answer_elt(question_choice, pp_answer, 'ID', 'id')
    pp_answer = add_answer_elt(question_choice, pp_answer, 'Text', 'text')
    pp_answer = add_mc_response_type(pp_answer)
    pp_answer = add_mc_answer_letter(question_choice, pp_answer)
    pp_answer = add_mc_value_and_feedback(question, pp_answer, pp_answer.findtext('letter'))
    return pp_answer


def process_msa_question(question):
    question_parts = question.xpath('Parts/QuestionPart')
    feedback = []
    for question_part in question_parts:
        answers = []
        question_part_number = question_part.findtext('Number')
        for question_answer in question_part.xpath('Answers/QuestionAnswer'):
            if is_sa_answer(question_answer):
                answers.append(question_answer.findtext('Text'))
            elif is_sa_feedback(question_answer):
                fb = '<p>'
                fb += question_part_number
                fb += ': '
                fb += question_answer.findtext('Feedback')
                fb += '</p>'
                feedback.append(fb)
        pp_answers = etree.Element('pp_answers')
        pp_answers.text = '|'.join(answers)
        question_part.insert(0, pp_answers)
        pp_regex = etree.Element('pp_is_regex')
        if len(answers) > 1:
            pp_regex.text = 'True'
        else:
            pp_regex.text = 'False'
        question_part.insert(0, pp_regex)
        pp_value = etree.Element('pp_value')
        value = 100.0 / len(question_parts)
        pp_value.text = "{:13.10f}".format(value)
        question_part.insert(1, pp_value)
    pp_feedback = etree.Element('pp_feedback')
    pp_feedback.text = ''.join(feedback)
    question.insert(0, pp_feedback)


def process_cpd_question(question):
    convert_cpd_question_to_msa(question)


def convert_cpd_question_to_msa(question):
    set_question_type_to_msa(question)
    convert_all_question_parts_to_sa(question)
    process_msa_question(question)


def set_question_type_to_msa(question):
    question.find('Type').text = Q_TYPES[Q_TYPE_MULTISHORTANSWER][Q_TYPE_NUMBER]


def convert_all_question_parts_to_sa(question):
    question_parts = question.xpath('Parts/QuestionPart')
    for question_part in question_parts:
        if is_sa_question_part(question_part):
            add_initial_br_tag(question_part)
        elif is_tf_question_part(question_part):
            convert_tf_question_part_to_sa(question_part)
        elif is_mc_question_part(question_part):
            convert_mc_question_part_to_sa(question_part)
        else:
            logging.error('Question part type not found', question.findtext('Title'))
            logging.error(question_part.findtext('Type'))


def add_initial_br_tag(question_part):
    text_elt = question_part.find('Text')
    text_elt.text = ''.join(['<BR><BR>', text_elt.text])


def is_sa_question_part(question_part):
    return is_question_part_type(question_part, Q_TYPE_SHORTANSWER)


def is_tf_question_part(question_part):
    return is_question_part_type(question_part, Q_TYPE_TRUEFALSE)


def is_mc_question_part(question_part):
    return is_question_part_type(question_part, Q_TYPE_MULTICHOICE)


def is_question_part_type(question_part, question_part_type):
    q_part_type = question_part.findtext('Type')
    return q_part_type == Q_TYPES[question_part_type][Q_TYPE_NUMBER]


def convert_tf_question_part_to_sa(question_part):
    replace_question_part_properties_with_sa(question_part)
    add_tf_flag(question_part)
    replace_incorrect_tf_question_answer_text(question_part)
    insert_tf_sa_instruction(question_part)
    remove_choices(question_part)


def convert_mc_question_part_to_sa(question_part):
    replace_question_part_properties_with_sa(question_part)
    replace_mc_question_part_with_sa(question_part)
    insert_mc_sa_instruction(question_part)
    remove_all_incorrect_question_answers(question_part)


def remove_all_incorrect_question_answers(question_part):
    answers = question_part.find('Answers')
    for question_answer in answers.findall('QuestionAnswer'):
        if is_sa_answer(question_answer) and is_incorrect_answer(question_answer):
            answers.remove(question_answer)


def replace_question_part_properties_with_sa(question_part):
    set_child_element_text(question_part, 'ShortAnsIgnoreCase', 'True')
    set_child_element_text(question_part, 'ChoicesType', '0')
    set_child_element_text(question_part, 'Type', '3')


def add_tf_flag(question_part):
    tf_flag = etree.Element('pp_is_tf')
    tf_flag.text = 'True'
    question_part.insert(0, tf_flag)


def replace_incorrect_tf_question_answer_text(question_part):
    try:
        incorrect_answer = question_part.xpath('Answers/QuestionAnswer[Value=0]')[0]
        incorrect_answer.find('Text').text = ''
    except IndexError:
        pass


def replace_mc_answer_elts_with_sa(question_part):
    replace_correct_mc_answer_elts_with_sa(question_part)
    replace_incorrect_tf_answer_elts_with_sa(question_part)


def replace_correct_mc_answer_elts_with_sa(question_part):
    correct_answer_elt = question_part.xpath('Answers/QuestionAnswer[Value=1]')[0]
    answer_text = correct_answer_elt.findtext('Text')
    set_child_element_text(correct_answer_elt, 'Value', '1')
    set_child_element_text(correct_answer_elt, 'Text', answer_text)
    set_child_element_text(correct_answer_elt, 'Feedback', '')


def remove_choices(question_part):
    for sub in question_part.iterchildren('Choices'):
        question_part.remove(sub)


def set_child_element_text(parent_elt, child_elt_name, text_value):
    parent_elt.find(child_elt_name).text = text_value


def insert_tf_sa_instruction(question_part):
    instruction = "['t'=True 'f'=False]"
    append_to_question_text(question_part, instruction)


def insert_mc_sa_instruction(question_part):
    instruction = "[enter letter of correct answer]"
    append_to_question_text(question_part, instruction)


def append_to_question_text(question_part, string_to_append):
    text_elt = question_part.find('Text')
    if text_elt is not None:
        text_elt.text += string_to_append


def replace_mc_question_part_with_sa(question_part):
    ol = get_choices_as_ordered_list(question_part)
    append_to_question_text(question_part, ol)


def get_choices_as_ordered_list(question_part):
    ol = HTML('ol')
    choices = get_choices(question_part)
    for choice in choices:
        li = ol.li(style='list-style-type:upper-alpha')
        li.text(choice.findtext('Text'))
    return unicode(ol)


def get_choices(question_part):
    choices = question_part.xpath('Choices/QuestionChoice')
    choices.sort(key=lambda choice: choice.findtext('Number'))
    return choices


def process_pe_question(question):
    parser_expression = question.find('ParserExpression')
    replace_illegal_variable_names(question)
    pe_variables = get_pe_variables(parser_expression)
    formula = get_formula(question, pe_variables)
    formula = linearize(formula, pe_variables)
    add_formula(formula, parser_expression)
    add_variables(parser_expression)
    add_decimal_places(parser_expression)
    add_feedback(question)
    record_question(question)


def replace_illegal_variable_names(question):
    replace_illegal_pe_variable_names(question)
    replace_illegal_formula_variable_names(question)


def replace_illegal_pe_variable_names(question):
    parser_expression = question.find('ParserExpression')
    pe_text = parser_expression.text
    parser_expression.text = replace_illegal_variable_names_in_text(pe_text)


def replace_illegal_formula_variable_names(question):
    answer_text_elt = get_answer_text_node(question)
    answer_text = answer_text_elt.text
    answer_text_elt.text = replace_illegal_variable_names_in_text(answer_text)


def replace_illegal_variable_names_in_text(text):
    global VARIABLE_REPLACEMENT_E
    pattern = r'\b[eE]\b'
    reworked_text = re.sub(pattern, VARIABLE_REPLACEMENT_E, text)
    return reworked_text


def add_feedback(question):
    feedback = etree.Element('pp_feedback')
    feedback_elts = question.xpath('Parts/QuestionPart/Answers/QuestionAnswer/Feedback[text()!=""]')
    if len(feedback_elts) > 0:
        feedback_text = question.xpath('Parts/QuestionPart/Answers/QuestionAnswer/Feedback[text()!=""]')[0].text
    else:
        feedback_text = ''
    feedback.text = feedback_text
    question.append(feedback)


def add_decimal_places(parser_expression):
    decimal_places = etree.Element('pp_decimal_places')
    decimal_places.text = get_max_decimal_places(parser_expression)
    parser_expression.append(decimal_places)


def get_max_decimal_places(parser_expression):
    decimal_places = parser_expression.xpath('pp_variables/pp_variable/pp_var_decimal_places/text()')
    try:
        max_decimal_places = max(decimal_places)
    except ValueError:
        max_decimal_places = '0'
    return max_decimal_places


def get_formula(question, pe_variables):
    answer_text = get_answer_text(question)
    answer_var_names = find_var_names(answer_text)
    if answer_var_names is not None and len(answer_var_names) > 0:
        formula = find_pe_value_for_name(answer_var_names[0], pe_variables)
    else:
        formula = answer_text
    return formula


def add_formula(formula_text, parser_expression):
    formula = etree.Element('pp_formula')
    formula.text = formula_text
    parser_expression.append(formula)


def linearize(expression, pe_variables):
    linear_expression = expression
    name_data = get_next_name(linear_expression)
    if name_data:
        name = name_data[0]
        start_index = name_data[1]
        end_index = name_data[2]
        if name == 'int':
            if is_int_function_call(linear_expression):
                linear_expression = replace_int_function_call(linear_expression)
                return linearize(linear_expression, pe_variables)
        elif name == 'sqrt':
            if is_sqrt_function_call(linear_expression):
                linear_expression = replace_sqrt_function_call(linear_expression)
                return linearize(linear_expression, pe_variables)
        elif name == 'sqr':
            start = expression[0:start_index]
            remainder = expression[end_index:]
            linear_expression = ''.join([start, name, linearize(remainder, pe_variables)])
        elif name in pe_variables:
            start = expression[0:start_index]
            name = "{{{}}}".format(name)
            remainder = expression[end_index:]
            linear_expression = ''.join([start, name, linearize(remainder, pe_variables)])
    return linear_expression


def get_next_name(expression):
    next_name = None
    pattern = get_re_pattern_variable()
    match = re.search(pattern, expression)
    if match:
        next_name = [match.group(), match.start(), match.end()]
    return next_name


def is_sqrt_function_call(expression):
    is_sqrt_call = is_function_call(expression, 'sqrt')
    return is_sqrt_call


def is_int_function_call(expression):
    is_int_call = is_function_call(expression, 'int')
    return is_int_call


def is_function_call(expression, function_name):
    pattern = r"^\W*\b{}\s*\(".format(function_name)
    match = re.match(pattern,expression)
    return match

def is_round_function_call(expression):
    pattern = re.compile('round(?=\()')
    match = pattern.search(expression)
    return match


def replace_int_function_call(expression):
    START = 0
    ARGS = 2
    END = 3
    expression_parts = split_int_call(expression)
    start = expression_parts[START]
    end = expression_parts[END]
    args_replacement = get_int_call_replacement(expression_parts[ARGS])
    reworked_expression = "{}{}{}".format(start, args_replacement, end)
    return reworked_expression


def replace_sqrt_function_call(expression):
    pattern = r'sqrt\('
    reworked_expression = re.sub(pattern, 'sqr(', expression)
    return reworked_expression


def get_int_call_replacement(args_string):
    replacement = "({} - ({} % 1.0))".format(args_string, args_string)
    return replacement


def split_int_call(expression):
    pattern = re.compile('(.*)(int(?=\())(.*)')
    match = pattern.search(expression)
    expression_start = match.group(1)
    expression_name = match.group(2)
    expression_remainder = match.group(3)
    arg_parts = balance_parens(expression_remainder)
    expression_args = arg_parts[0]
    expression_end = arg_parts[1]
    int_call = [expression_start, expression_name, expression_args, expression_end]
    return int_call


def balance_parens(expression):
    """Return string with balanced parentheses"""
    last_paren_index = find_last_paren_index(expression)
    parts = [expression[:last_paren_index + 1], expression[last_paren_index + 1:]]
    return parts


def find_last_paren_index(expression):
    last_paren_index = -1
    balance = 0
    for index, character in enumerate(expression):
        if character == '(':
            balance += 1
        elif character == ')':
            balance -= 1
            if balance == 0:
                last_paren_index = index
                break
    return last_paren_index


def is_random_pe_variable(value):
    is_random_variable = 'rndnum(' in value
    return is_random_variable


def search_expression_for_variable_names(expression):
    pattern = get_re_pattern_variable()
    variable_name = pattern.search(expression).group()
    return variable_name


def find_var_names(text):
    pattern = get_re_pattern_variable()
    pattern = r'\b([a-zA-Z]+[\d_]*[\w\d]*)'
    var_names = re.findall(pattern, text)
    return var_names


def get_answer_text(question):
    answer_text_node = get_answer_text_node(question)
    answer_text = answer_text_node.text
    return answer_text


def get_answer_text_node(question):
    answer_text_nodes = question.xpath('Parts/QuestionPart/Answers/QuestionAnswer/Text[normalize-space(text()) != ""]')
    answer_text_node = answer_text_nodes[0]
    return answer_text_node


def find_pe_value_for_name(name, pe_variables):
    value = ''
    name_lc = name.lower()
    name_uc = name.upper()
    if name_lc in pe_variables:
        value = pe_variables[name_lc]
    elif name_uc in pe_variables:
        value = pe_variables[name_uc]
    return value


def add_variables(parser_expression):
    variables = etree.Element('pp_variables')
    random_variables = get_random_variables(parser_expression)
    for random_variable_name in random_variables:
        random_params = get_random_params(random_variables[random_variable_name])
        variable = build_random_variable()
        set_variable_properties(variable, random_variable_name, random_params)
        variables.append(variable)
    parser_expression.append(variables)


def get_random_params(random_variable_value):
    pattern = re.compile('\([+-]?\s*(\d*\.?\d+)\s*,?\s*([+-]?\d*\.?\d+)\s*,?\s*([+-]?\d*\.?\d+)\s*\)')
    match = pattern.search(random_variable_value)
    params = {'min': match.group(1), 'max': match.group(2), 'step': match.group(3)}
    return params


def get_random_variables(parser_expression):
    variables = get_pe_variables(parser_expression)
    variables = {name: value for name, value in variables.items() if 'rndnum(' in variables[name]}
    return variables


def get_pe_variables(parser_expression):
    variables = {}
    statements = get_pe_statements(parser_expression)
    for statement in statements:
        if is_valid_pe_variable_statement(statement):
            parts = statement.split('=')
            name = parts[0].strip().lower()
            value = parts[1].strip().lower()
            variables[name] = value
    return variables


def is_valid_pe_variable_statement(statement):
    is_valid_pe_variable_statement = True
    if is_substitute_statement(statement) or is_format_statement(statement) or is_round_statement(statement):
        is_valid_pe_variable_statement = False
    return is_valid_pe_variable_statement


def is_substitute_statement(statement):
    is_substitute_statement = is_matching_statement(statement, 'substitute\s*\(')
    return is_substitute_statement


def is_format_statement(statement):
    is_format_statement = is_matching_statement(statement, 'format\s*\(')
    return is_format_statement


def is_round_statement(statement):
    is_round_statement = is_matching_statement(statement, 'round\s*\(')
    return is_round_statement


def is_matching_statement(statement, match_text):
    pattern = re.compile(match_text)
    is_matching_statement = pattern.search(statement)
    return is_matching_statement


def get_pe_statements(parser_expression):
    parser_expression_text = parser_expression.text.strip()
    statements = parser_expression_text.split(';')
    statements = [statement.strip() for statement in statements if statement is not '']
    return statements


def build_random_variable():
    random_variable = etree.Element('pp_variable')
    variable_name = etree.Element('pp_var_name')
    variable_min = etree.Element('pp_var_min')
    variable_max = etree.Element('pp_var_max')
    variable_step = etree.Element('pp_var_step')
    variable_decimal_places = etree.Element('pp_var_decimal_places')
    random_variable.append(variable_name)
    random_variable.append(variable_min)
    random_variable.append(variable_max)
    random_variable.append(variable_step)
    random_variable.append(variable_decimal_places)
    return random_variable


def set_variable_properties(variable, random_variable_name, random_params):
    variable.find('pp_var_name').text = random_variable_name
    random_min =  random_params['min']
    random_max = random_params['max']
    random_step = random_params['step']
    variable.find('pp_var_min').text = random_min
    variable.find('pp_var_max').text = random_max
    variable.find('pp_var_step').text = random_step
    variable.find('pp_var_decimal_places').text = get_random_variable_decimal_places(random_min, random_max, random_step)


def get_random_variable_decimal_places(random_min, random_max, random_step):
    num_decimal_places = 0
    for number in [random_min, random_max, random_step]:
        mantissa_length = get_mantissa_length(number)
        if mantissa_length > num_decimal_places:
            num_decimal_places = mantissa_length
    num_decimal_places_as_string = str(num_decimal_places)
    return num_decimal_places_as_string


def get_mantissa_length(number):
    mantissa_length = 0
    decimal = '.'
    if decimal in number:
        parts = number.split(decimal)
        mantissa = parts[-1]
        mantissa_length = len(mantissa)
    return mantissa_length


def is_d2l_compatible_pe_question(question):
    is_compatible = False
    if is_single_part_question(question):
        pe = question.findtext('ParserExpression')
        if is_d2l_compatible_pe(pe):
            is_compatible = True
    return is_compatible


def is_d2l_compatible_pe(parser_expression):
    no_braces = '{' not in parser_expression
    pattern = r'\bif\s*\('
    match = re.search(pattern, parser_expression)
    no_if = match is None
    return no_braces and no_if


#insert block below in function
#    if skip_question(num):
#        return
#    else:
#        record_question(question)
custom_count = 0
def skip_question(num_questions):
    global custom_count
    custom_count += 1
    return custom_count > num_questions


__custom_question_titles = {}
def record_question(question):
    count = 0
    for titles in __custom_question_titles:
        count += len(__custom_question_titles[titles])
    module_title = p2_unicode_utils.to_str(question.xpath('ancestor::Assessment/Title/text()')[0])
    module_title += '-'
    module_title += p2_unicode_utils.to_str(question.xpath('ancestor::Assessment/ID/text()')[0])
    question_title = p2_unicode_utils.to_str(question.findtext('Title'))
#    question_title += ' : '
#    question_title += str(count + 1)

    if module_title not in __custom_question_titles:
        __custom_question_titles[module_title] = []
    __custom_question_titles[module_title].append(question_title)


def write_it():
    with open('custom questions.txt', 'w') as f:
        f.truncate()
        for line in __custom_question_titles:
            f.write(line)
            f.write("\n")
            for title in __custom_question_titles[line]:
                f.write("\t")
                f.write(title)
                f.write("\n")
            f.write("\n")


def process_mr_question(question):
    '''Seems the few MR question coming in from TLM are mistakes. Should be MC questions.'''
    process_mc_question(question)


def process_tf_question(question):
    pp_answers = etree.Element('pp_answers')
    for question_answer in question.xpath('Parts/QuestionPart/Answers/QuestionAnswer'):
        pp_answer = process_tf_answer(question, question_answer)
        pp_answers.append(pp_answer)
    pp_answers = check_tf_answer_order(pp_answers)
    question.insert(0, pp_answers)


def process_tf_answer(question, question_answer):
    pp_answer = etree.Element('pp_answer')
    pp_answer = add_tf_response_number(question_answer, pp_answer)
    pp_answer = add_answer_elt(question_answer, pp_answer, 'ID', 'id')
    pp_answer = add_answer_elt(question_answer, pp_answer, 'Value', 'value')
    pp_answer = add_answer_elt(question_answer, pp_answer, 'Feedback', 'feedback')
    pp_answer = add_tf_response_text(question_answer, pp_answer)
    pp_answer = add_tf_response_type(pp_answer)
    return pp_answer


def check_tf_answer_order(pp_answers):
    first_answer = pp_answers.find('pp_answer')
    if first_answer.findtext('text').lower() in LC_FALSE_VALUES:
        pp_answers.append(first_answer)
    return pp_answers


def process_sa_question(question):
    question_parts = question.xpath('Parts/QuestionPart')
    num_parts = len(question_parts)
    if num_parts > 0:
        process_sa_answers(question_parts[0])
    if not num_parts == 1:
        logging.error('SA question not = 1 [' + str(num_parts) + '] ' + question.findtext('Title'))


def process_sa_answers(question_part):
    is_msa = is_multiple_short_answer_question(question_part.xpath('ancestor::Question')[0])
    question_answers = get_question_answers(question_part)
    process_sa_answer_values(question_answers, is_msa)


def process_sa_answer_values(question_answers, is_msa=False):
    if is_msa:
        total = 0.0
        for question_answer in question_answers:
            total += float(question_answer.findtext('Value'))
        for question_answer in question_answers:
            value = float(question_answer.findtext('Value'))
            new_value = (value/total)
            question_answer.find('Value').text = "{:13.10f}".format(new_value)
    else:
        greatest_value = find_greatest_question_answer_value(question_answers)
        for question_answer in question_answers:
            value = float(question_answer.findtext('Value'))
            new_value = 100.0
            if value < greatest_value:
                new_value = value/greatest_value
            question_answer.find('Value').text = "{:13.10f}".format(new_value)


def find_greatest_question_answer_value(question_answers):
    greatest_value = 0
    for question_answer in question_answers:
        value = int(question_answer.findtext('Value'))
        if value > greatest_value:
            greatest_value = value
    return greatest_value


def get_question_answers(question_part):
    return question_part.xpath('Answers/QuestionAnswer[Value > 0]')


def is_sa_feedback(question_answer):
    return is_sa_element(question_answer, 'Feedback')


def is_sa_element(question_answer, element_name):
    try:
        is_sa_element = len(question_answer.findtext(element_name)) > 0
    except:
        is_sa_element = False
    return is_sa_element


def is_sa_answer(question_answer):
    return is_sa_element(question_answer, 'Text')


def is_incorrect_answer(question_answer):
    return question_answer.findtext('Value') == '0'


def process_sa_answer(question_answer):
    pp_answer = etree.Element('pp_answer')
    add_sa_answer_text(question_answer, pp_answer)
    add_sa_answer_value(question_answer, pp_answer)
    return pp_answer


def add_sa_answer_text(question_answer, pp_answer):
    add_sa_text(question_answer, pp_answer, 'Text')


def add_sa_answer_value(question_answer, pp_answer):
    pp_value = etree.Element('value')
    pp_value.text = question_answer.findtext('Value')
    pp_answer.append(pp_value)


def init_sa_feedback():
    pp_feedback = etree.Element('pp_feedback')
    pp_text = etree.Element('text')
    pp_text.text = ''
    pp_feedback.append(pp_text)
    return pp_feedback


def update_sa_feedback(question_answer, pp_feedback):
    feedback = question_answer.findtext('Feedback')
    if feedback:
        text_elt = pp_feedback.find('text')
        if text_elt is not None:
            text_elt.text = feedback


def add_sa_feedback_text(question_answer, pp_answer):
    add_sa_text(question_answer, pp_answer, 'Feedback')


def add_sa_text(question_answer, pp_answer, text_elt_name):
    pp_text = etree.Element('text')
    pp_text.text = question_answer.findtext(text_elt_name)
    pp_answer.append(pp_text)


def get_ignore_case(question):
    ignore_case = question.findtext('Parts/QuestionPart/ShortAnsIgnoreCase')
    if not ignore_case:
        ignore_case = 'False'
    return ignore_case


def add_sa_text_value_and_feedback(question, pp_answer):
    matching_question_answer_elt = find_question_answer_elt_by_text_value(question, choice_letter)
    if matching_question_answer_elt is not None:
        value = matching_question_answer_elt.findtext('Value')
        fb = matching_question_answer_elt.findtext('Feedback')
        use_custom_fb = matching_question_answer_elt.findtext('UseCustomFeedback')
    else:
        value = '0'
        fb = ''
        use_custom_fb = 'False'
    if use_custom_fb == 'False':
        fb = find_default_feedback(question)
    value_elt = etree.Element('value')
    value_elt.text = value
    pp_answer.append(value_elt)
    fb_elt = etree.Element('feedback')
    fb_elt.text = fb
    pp_answer.append(fb_elt)
    use_custom_fb_elt = etree.Element('usecustomfeedback')
    use_custom_fb_elt.text = use_custom_fb
    pp_answer.append(use_custom_fb_elt)
    return pp_answer


def add_tf_question_letter_elt(question_answer_elt, pp_answer):
    question_letter_elt = etree.Element('letter')
    question_letter_elt.text = ''
    question_text = question_answer_elt.findtext('Text').strip().upper()
    if question_text == 'T':
        question_letter_elt.text = 'T'
    elif question_text == 'F':
        question_letter_elt.text = 'F'
    pp_answer.append(question_letter_elt)
    return pp_answer


def add_tf_question_text_elt(pp_answer):
    question_text_elt = etree.Element('text')
    question_text_elt.text = ''
    question_letter = pp_answer.findtext('letter')
    if question_letter == 'T':
        question_text_elt.text = 'True'
    elif question_letter == 'F':
        question_text_elt.text = 'False'
    pp_answer.append(question_text_elt)
    return pp_answer


def add_tf_question_value_elt(question_answer_elt, pp_answer):
    question_value_elt = etree.Element('value')
    question_value_elt.text = question_answer_elt.findtext('Value')
    pp_answer.append(question_value_elt)
    return pp_answer



def add_tf_question_feedback_elts(question_answer_elt, pp_answer):
    question_fb_elt = etree.Element('feedback')
    question_fb_elt.text = question_answer_elt.findtext('Feedback')
    pp_answer.append(question_fb_elt)
    question_use_custom_fb_elt = etree.Element('usecustomfeedback')
    question_use_custom_fb_elt.text = question_answer_elt.findtext('UseCustomFeedback')
    pp_answer.append(question_use_custom_fb_elt)
    return pp_answer


def add_mc_response_type(pp_answer):
    response_type_elt = etree.Element('responsetype')
    response_type_elt.text = 'text/html'
    pp_answer.append(response_type_elt)
    return pp_answer


def add_tf_response_number(question_answer, pp_answer):
    response_number_elt = etree.Element('number')
    response_number_elt.text = str(question_answer.getparent().index(question_answer) + 1)
    pp_answer.append(response_number_elt)
    return pp_answer


def add_tf_response_type(pp_answer):
    response_type_elt = etree.Element('responsetype')
    response_type_elt.text = 'text/plain'
    pp_answer.append(response_type_elt)
    return pp_answer


def add_tf_response_text(question_answer, pp_answer):
    resp_text = question_answer.findtext('Text')
    if resp_text.lower() in LC_TRUE_VALUES:
        resp_text = 'True'
    elif resp_text.lower() in LC_FALSE_VALUES:
        resp_text = 'False'
    elif resp_text == '':
        resp_text = get_tf_text_for_blank_value(question_answer)
    resp_text_elt = etree.Element('text')
    resp_text_elt.text = resp_text
    pp_answer.append(resp_text_elt)
    return pp_answer


def get_tf_text_for_blank_value(question_answer):
    answer_text = ''
    if question_answer.getprevious() is not None:
        answer_text = get_tf_text_inverse_of(question_answer.getprevious().findtext('Text'))
    elif question_answer.getnext() is not None:
        answer_text = get_tf_text_inverse_of(question_answer.getnext().findtext('Text'))
    return answer_text


def get_tf_text_inverse_of(tf_answer_text):
    answer_text = 'Undetermined'
    if tf_answer_text.lower() in LC_TRUE_VALUES:
        answer_text = 'False'
    elif tf_answer_text.lower() in LC_FALSE_VALUES:
        answer_text = 'True'
    return answer_text


def add_answer_elt(question_choice, pp_answer, src_elt_name, dest_elt_name):
    dest_elt = etree.Element(dest_elt_name)
    dest_elt.text = question_choice.findtext(src_elt_name)
    pp_answer.append(dest_elt)
    return pp_answer


def add_mc_answer_letter(question_choice, pp_answer):
    letters = ('', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
    letter_elt = etree.Element('letter')
    number_text = question_choice.findtext('Number')
    letter_index = int(number_text)
    letter_elt.text = letters[letter_index]
    pp_answer.append(letter_elt)
    return pp_answer


def add_mc_value_and_feedback(question, pp_answer, choice_letter):
    matching_question_answer_elt = find_question_answer_elt_by_text_value(question, choice_letter)
    if matching_question_answer_elt is not None:
        value = matching_question_answer_elt.findtext('Value')
        fb = matching_question_answer_elt.findtext('Feedback')
        use_custom_fb = matching_question_answer_elt.findtext('UseCustomFeedback')
    else:
        value = '0'
        fb = ''
        use_custom_fb = 'False'
    if use_custom_fb == 'False':
        fb = find_default_feedback(question)
    value_elt = etree.Element('value')
    value_elt.text = value
    pp_answer.append(value_elt)
    fb_elt = etree.Element('feedback')
    fb_elt.text = fb
    pp_answer.append(fb_elt)
    use_custom_fb_elt = etree.Element('usecustomfeedback')
    use_custom_fb_elt.text = use_custom_fb
    pp_answer.append(use_custom_fb_elt)
    return pp_answer


def find_default_feedback(question):
    default_feedback = ''
    default_question_answer_elt = find_question_answer_elt_by_text_value(question, '')
    if default_question_answer_elt is None:
        default_question_answer_elts = question.xpath('Parts/QuestionPart/Answers/QuestionAnswer[not(./Text)]')
        if default_question_answer_elts:
            default_question_answer_elt = default_question_answer_elts[0]
    if default_question_answer_elt is not None:
        default_feedback = default_question_answer_elt.findtext('Feedback')
    return default_feedback


def find_question_answer_elt_by_text_value(question, text_val):
    xpath_expr = ''.join(['Parts/QuestionPart/Answers/QuestionAnswer[Text = "', text_val, '"]'])
    question_answer_elts = question.xpath(xpath_expr)
    if question_answer_elts:
        question_answer_elt = question_answer_elts[0]
    else:
        question_answer_elt = None
    return question_answer_elt


def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def get_re_pattern_variable():
    global RE_PATTERN_VARIABLE
    return RE_PATTERN_VARIABLE
