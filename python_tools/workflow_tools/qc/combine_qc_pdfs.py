import argparse
from PyPDF2 import PdfFileMerger


FINAL_QC_FILENAME = 'main_qc.pdf'


def combine_pdfs(args):
    merger = PdfFileMerger()

    merger.append(open(args.std_qc, 'rb'))
    merger.append(open(args.noise_alt_percent, 'rb'))
    merger.append(open(args.noise_contributing_sites, 'rb'))
    merger.append(open(args.fingerprinting_qc, 'rb'))

    # Gender plot only produced if there are mismatches
    if args.gender_check:
        merger.append(open(args.gender_check, 'rb'))

    with open('./' + FINAL_QC_FILENAME, 'wb') as fout:
        merger.write(fout)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--std_qc", required=True)
    parser.add_argument("-a", "--noise_alt_percent", required=True)
    parser.add_argument("-c", "--noise_contributing_sites", required=False)
    parser.add_argument("-f", "--fingerprinting_qc", required=False)
    parser.add_argument("-g", "--gender_check", required=False)
    return parser.parse_args()


def main():
    args= parse_arguments()
    combine_pdfs(args)

if __name__ == '__main__':
    main()
