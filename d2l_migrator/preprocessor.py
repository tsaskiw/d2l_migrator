import sys, logging
from lxml import etree
import image_processor

Q_TYPE_ALL = 'ALL'
Q_TYPE_MULTICHOICE = 'MULTICHOICE'
Q_TYPE_MULTIRESPONSE = 'MULTIRESPONSE'
Q_TYPE_TRUEFALSE = 'TRUEFALSE'
Q_TYPE_SHORTANSWER = 'SHORTANSWER'
QUESTION_TYPES = {'1': Q_TYPE_MULTICHOICE, '2': Q_TYPE_MULTIRESPONSE, '3': Q_TYPE_SHORTANSWER, '4': Q_TYPE_TRUEFALSE}
QUESTION_TYPE_NUMBERS = {name: num for num, name in QUESTION_TYPES.items()}

def process(infile_path, base_url, outdir, question_type):
    ques_type = get_question_type(question_type)
    parser = etree.XMLParser(remove_blank_text=True)
    source_etree = etree.parse(infile_path, parser)
    course_code = source_etree.findtext('ECourse/Code')
    logging.info('\nProcessing ' + course_code)
    remove_assessments_without_question_type(ques_type, source_etree)
    remove_questions_other_than(ques_type, source_etree)
    assessment_count = int(source_etree.xpath('count(/TLMPackage/Assessment)'))
    logging.info('assessments: ' + str(assessment_count))
    result_etree = process_questions(source_etree, base_url, outdir)
    return result_etree

def get_question_type(question_type):
    ques_types = {'all': Q_TYPE_ALL, 'mc': Q_TYPE_MULTICHOICE, 'mr': Q_TYPE_MULTIRESPONSE, 'sa': Q_TYPE_SHORTANSWER, 'tf': Q_TYPE_TRUEFALSE}
    return ques_types[question_type]

def remove_assessments_without_question_type(question_type, source_etree):
    if question_type != Q_TYPE_ALL:
        assessments = source_etree.findall('//Assessment')
        question_type_number = QUESTION_TYPE_NUMBERS[question_type]
        for assessment in assessments:
            questions = assessment.xpath('descendant::Question[Type=' + question_type_number + ']')
            if not questions:
                assessment.getparent().remove(assessment)
            else:
                logging.info(''.join([assessment.findtext('Title'), ' : ', str(len(questions))]))

def remove_questions_other_than(question_type, source_etree):
    if question_type != Q_TYPE_ALL:
        question_type_number = QUESTION_TYPE_NUMBERS[question_type]
        assessments = source_etree.findall('//Assessment')
        for assessment in assessments:
            questions = assessment.xpath('descendant::Question[Type!=' + question_type_number + ']')
            for question in questions:
                question.getparent().remove(question)

def process_questions(intree, base_url, outdir):
    mc_question_count = 0
    mr_question_count = 0
    tf_question_count = 0
    sa_question_count = 0
    questions = intree.xpath('//Question[ancestor::Assessment and (Type=1 or Type=2 or Type=3 or Type=4)]')
    for question in questions:
        question_type = QUESTION_TYPES[question.findtext('Type')]
        if question_type == Q_TYPE_MULTICHOICE:
            process_mc_question(question)
            mc_question_count += 1
        if question_type == Q_TYPE_MULTIRESPONSE:
            process_mr_question(question)
            mr_question_count += 1
        elif question_type == Q_TYPE_SHORTANSWER:
            process_sa_question(question)
            sa_question_count += 1
        elif question_type == Q_TYPE_TRUEFALSE:
            process_tf_question(question)
            tf_question_count += 1
        image_processor.process_images(question, base_url, outdir)
    logging.info('mc = ' + str(mc_question_count) + ' mr = ' + str(mr_question_count) + ' tf = ' + str(tf_question_count) + ' sa = ' + str(sa_question_count) + ' tot = ' + str((mc_question_count + tf_question_count + sa_question_count)))
    return intree

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

def process_mr_question(question):
    process_mc_question(question)

def process_tf_question(question):
    pp_answers = etree.Element('pp_answers')
    for question_answer in question.xpath('Parts/QuestionPart/Answers/QuestionAnswer'):
        pp_answer = process_tf_answer(question, question_answer)
        pp_answers.append(pp_answer)
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

def process_sa_question(question):
    pp_ignore_case = etree.Element('pp_ignore_case')
    pp_ignore_case.text = get_ignore_case(question)
    pp_answers = etree.Element('pp_answers')
    pp_feedback = init_sa_feedback()
    for question_answer in question.xpath('Parts/QuestionPart/Answers/QuestionAnswer'):
        if is_sa_answer(question_answer):
            answer = process_sa_answer(question_answer)
            pp_answers.append(answer)
        elif is_sa_feedback(question_answer):
            update_sa_feedback(question_answer, pp_feedback)
    question.insert(0, pp_ignore_case)
    question.insert(1, pp_answers)
    question.insert(2, pp_feedback)

def is_sa_answer(question_answer):
    return is_sa_element(question_answer, 'Text')

def is_sa_feedback(question_answer):
    return is_sa_element(question_answer, 'Feedback')

def is_sa_element(question_answer, element_name):
    is_sa_element = len(question_answer.findtext(element_name)) > 0
    return is_sa_element

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
    if resp_text.lower() == 't':
        resp_text = 'True'
    elif resp_text.lower() == 'f':
        resp_text = 'False'
    resp_text_elt = etree.Element('text')
    resp_text_elt.text = resp_text
    pp_answer.append(resp_text_elt)
    return pp_answer

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
