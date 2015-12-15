import sys, getopt, os.path
import d2l_migrator


VALID_QUESTION_TYPES = ('all', 'cpd', 'mc', 'mr', 'msa', 'pe', 'sa', 'tf')


def collect_input(argv):
    infile = ''
    stylesheet = ''
    outdir = ''
    base_url = ''
    question_type = 'all'
    diffdir = ''
    question_list_file = ''
    try:
        opts, args = getopt.getopt(argv,"hi:s:o:b:q:d:l:",["ifile=","sfile=","odir=","base_url=", "question_type=", "diffdir=", "question_list_file="])
    except getopt.GetoptError:
        d2l_migrator.print_usage()
        sys.exit(2)
    if len(opts) < 5:
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
        elif opt in ("-d", "--diffdir"):
            diffdir = arg
        elif opt in ("-l", "--question_list"):
            question_list_file = arg
    return (infile, stylesheet, outdir, base_url, question_type, diffdir, question_list_file)

def validate_input(infile, stylesheet, outdir, base_url, question_type, diffdir, question_list_file):
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
    if question_type not in VALID_QUESTION_TYPES:
        invalid_params.append(question_type)
    if (diffdir and dir_doesnt_exist(diffdir)):
        invalid_params.append(diffdir)
    if (question_list_file and file_doesnt_exist(question_list_file)):
        invalid_params.append(question_list_file)
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
    return question_type not in VALID_QUESTION_TYPES
