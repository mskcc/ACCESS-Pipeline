import argparse
import datetime
import pandas as pd
from PyPDF2 import PdfFileMerger

from ...constants import *


def combine_pdfs(args):
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Grab the pool from the title file
    title_file = pd.read_csv(args.title_file, sep='\t')
    pool = title_file[TITLE_FILE__POOL_COLUMN].values[0]

    FINAL_QC_FILENAME = pool + '_' + date + '.pdf'

    merger = PdfFileMerger()

    for pdf in args.pdf_files:
        print(pdf)
        merger.append(open(pdf), 'rb')

    with open('./' + FINAL_QC_FILENAME, 'wb') as fout:
        merger.write(fout)


def main():
    parser = argparse.ArgumentParser(prog='Combine PDF files into one PDF', usage='%(prog)s [options]')
    parser.add_argument('-t', '--title_file')
    parser.add_argument('pdf_files', nargs='+', help='bar help')
    args = parser.parse_args()
    combine_pdfs(args)


if __name__ == '__main__':
    main()
