import sys, logging
from lxml import etree
import image_processor

Q_TYPE_MULTICHOICE = 'MULTICHOICE'
Q_TYPE_TRUEFALSE = 'TRUEFALSE'
QUESTION_TYPES = {'1': Q_TYPE_MULTICHOICE, '4': Q_TYPE_TRUEFALSE}

def process(infile_path, base_url, outdir):
    parser = etree.XMLParser(remove_blank_text=True)
    source_etree = etree.parse(infile_path, parser)
    course_code = source_etree.findtext('ECourse/Code')
    logging.info('\nProcessing ' + course_code)
    assessment_count = source_etree.xpath('count(/TLMPackage/Assessment)')
    logging.info('assessments: ' + str(int(assessment_count)))
    result_etree = process_questions(source_etree, base_url, outdir)
    return result_etree

def process_questions(intree, base_url, outdir):
    mc_question_count = 0
    tf_question_count = 0
    mc_tf_questions = intree.xpath('//Question[ancestor::Assessment and (Type=1 or Type=4)]')
    for question in mc_tf_questions:
        pp_answers = etree.Element('pp_answers')
        for question_choice in question.xpath('Parts/QuestionPart/Choices/QuestionChoice'):
            question_type = QUESTION_TYPES[question.findtext('Type')]
            pp_answer = etree.Element('pp_answer')
            if question_type == Q_TYPE_MULTICHOICE:
                pp_answer = process_mc_question(question, question_choice, pp_answer)
                mc_question_count += 1
            elif question_type == Q_TYPE_TRUEFALSE:
                pp_answer = process_tf_question(question, question_choice, pp_answer)
                tf_question_count += 1
            pp_answers.append(pp_answer)
        question.insert(0, pp_answers)
        image_processor.process_images(question, base_url, outdir)
    logging.info('mc = ' + str(mc_question_count) + ' tf = ' + str(tf_question_count) + ' tot = ' + str((mc_question_count + tf_question_count)))
    return intree

def process_mc_question(question, question_choice, pp_answer):
    pp_answer = add_answer_elt(question_choice, pp_answer, 'Number', 'number')
    pp_answer = add_answer_elt(question_choice, pp_answer, 'ID', 'id')
    pp_answer = add_answer_elt(question_choice, pp_answer, 'Text', 'text')
    pp_answer = add_mc_response_type(pp_answer)
    pp_answer = add_mc_answer_letter(question_choice, pp_answer)
    pp_answer = add_mc_value_and_feedback(question, pp_answer, pp_answer.findtext('letter'))
    return pp_answer

def process_tf_question(question, question_choice, pp_answer):
    pp_answer = add_answer_elt(question_choice, pp_answer, 'Number', 'number')
    pp_answer = add_answer_elt(question_choice, pp_answer, 'ID', 'id')
    pp_answer = add_tf_text_letter_value_and_feedback(question, pp_answer)
    pp_answer = add_tf_response_type(pp_answer)
    return pp_answer

def add_tf_text_letter_value_and_feedback(question, pp_answer):
    question_answer_elt = question.xpath('Parts/QuestionPart/Answers/QuestionAnswer[position() = ' + pp_answer.findtext('number') + ']')
    if question_answer_elt:
        question_answer_elt = question_answer_elt[0]
        pp_answer = add_tf_question_letter_elt(question_answer_elt, pp_answer)
        pp_answer = add_tf_question_text_elt(pp_answer)
        pp_answer = add_tf_question_value_elt(question_answer_elt, pp_answer)
        pp_answer = add_tf_question_feedback_elts(question_answer_elt, pp_answer)
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

def add_tf_response_type(pp_answer):
    response_type_elt = etree.Element('responsetype')
    response_type_elt.text = 'text/plain'
    pp_answer.append(response_type_elt)
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
