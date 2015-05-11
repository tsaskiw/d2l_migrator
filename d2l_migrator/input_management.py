import sys, getopt, os.path
import d2l_migrator

def collect_input(argv):
    infile = ''
    stylesheet = ''
    outdir = ''
    base_url = ''
    question_type = 'all'

    try:
        opts, args = getopt.getopt(argv,"hi:s:o:b:q:",["ifile=","sfile=","odir=","base_url=", "question_type="])
    except getopt.GetoptError:
        d2l_migrator.print_usage()
        sys.exit(2)

    if len(opts) < 4:
        d2l_migrator.print_usage('Parameter(s) missing. Usage:')
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            d2l_migrator.print_usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = arg
        elif opt in ("-s", "--sfile"):
            stylesheet = arg
        elif opt in ("-o", "--odir"):
            outdir = arg
        elif opt in ("-b", "--base_url"):
            base_url = arg
        elif opt in ("-q", "--question_type"):
            question_type = arg

    return (infile, stylesheet, outdir, base_url, question_type)

def validate_input(infile, stylesheet, outdir, base_url, question_type):
    input_is_valid = True
    invalid_params = []
    if file_doesnt_exist(infile):
        invalid_params.append(infile)
    if file_doesnt_exist(stylesheet):
        invalid_params.append(stylesheet)
    if dir_doesnt_exist(outdir):
        try:
            os.makedirs(outdir)
        except OSError:
            invalid_params.append(outdir)
    if dir_doesnt_exist(base_url):
        invalid_params.append(base_url)
    if question_type_not_found(question_type):
        invalid_params.append(question_type)
    if len(invalid_params) > 0:
        input_is_valid = False
        for param in invalid_params:
            print('\n' + param + ' is not valid.')
    return input_is_valid

def file_doesnt_exist(file_path):
    return not (os.path.exists(file_path) and os.path.isfile(file_path))

def dir_doesnt_exist(dir_path):
    return not (os.path.exists(dir_path) and not os.path.isfile(dir_path))

def question_type_not_found(question_type):
    valid_question_types = ('all', 'mc', 'sa', 'tf')
    return question_type not in valid_question_types
