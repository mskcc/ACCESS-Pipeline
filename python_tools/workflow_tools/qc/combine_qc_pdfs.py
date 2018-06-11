import argparse
from PyPDF2 import PdfFileMerger


FINAL_QC_FILENAME = 'all_qc.pdf'


def combine_pdfs(args):
    merger = PdfFileMerger()

    for f in args.umi_qc:
        merger.append(open(f, 'rb'))

    merger.append(open(args.noise_alt_percent, 'rb'))
    merger.append(open(args.noise_contributing_sites, 'rb'))
    merger.append(open(args.fingerprinting_qc, 'rb'))

    with open('./' + FINAL_QC_FILENAME, 'wb') as fout:
        merger.write(fout)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--umi_qc", nargs='+', required=True)
    parser.add_argument("-a", "--noise_alt_percent", required=True)
    parser.add_argument("-c", "--noise_contributing_sites", required=False)
    parser.add_argument("-f", "--fingerprinting_qc", required=False)
    args = parser.parse_args()

    return args


def main():
    args= parse_arguments()
    combine_pdfs(args)

if __name__ == '__main__':
    main()
