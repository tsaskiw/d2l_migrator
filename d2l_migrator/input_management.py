import sys, getopt, os.path

def get_input(argv):
    infile, stylesheet, outfile, base_url = collect_input(argv)
    input_is_valid = validate_input(infile, stylesheet, outfile, base_url)
    if not input_is_valid:
        sys.exit()
    return (infile, stylesheet, outfile, base_url)

def collect_input(argv):
    infile = ''
    stylesheet = ''
    outfile = ''
    base_url = ''
    try:
        opts, args = getopt.getopt(argv,"hi:s:o:b:",["ifile=","sfile=","ofile=","base_url="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    if len(opts) != 4:
        print_usage('Parameter(s) missing. Usage:')
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = arg
        elif opt in ("-s", "--sfile"):
            stylesheet = arg
        elif opt in ("-o", "--ofile"):
            outfile = arg
        elif opt in ("-b", "--base_url"):
            base_url = arg

    return (infile, stylesheet, outfile, base_url)

def validate_input(infile, stylesheet, outfile, base_url):
    input_is_valid = True
    invalid_params = []
    if file_doesnt_exist(infile):
        invalid_params.append(infile)
    if file_doesnt_exist(stylesheet):
        invalid_params.append(stylesheet)
    if file_doesnt_exist(outfile):
        invalid_params.append(outfile)
    if dir_doesnt_exist(base_url):
        invalid_params.append(base_url)
    if len(invalid_params) > 0:
        input_is_valid = False
        for param in invalid_params:
            print('\n' + param + ' doesnt exist')
    return input_is_valid

def file_doesnt_exist(file_path):
    return not (os.path.exists(file_path) and os.path.isfile(file_path))

def dir_doesnt_exist(dir_path):
    return not (os.path.exists(dir_path) and not os.path.isfile(dir_path))

def print_usage(msg='Usage:'):
    print(msg)
    print('d2l_migrator.py -i <inputfile> -s <stylesheet> -o <outputfile> -b <baseurl>')
