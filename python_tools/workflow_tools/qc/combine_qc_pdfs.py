import logging
import argparse
import datetime
from PyPDF2 import PdfFileMerger


def combine_pdfs(args):
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    project_name = args.project_name.replace(' ', '')
    FINAL_QC_FILENAME = project_name + '_' + date + '.pdf'

    merger = PdfFileMerger()

    for pdf in args.pdf_files:
        logging.info(pdf)
        merger.append(open(pdf), 'rb')

    with open('./' + FINAL_QC_FILENAME, 'wb') as fout:
        merger.write(fout)


def main():
    parser = argparse.ArgumentParser(prog='Combine PDF files into one PDF', usage='%(prog)s [options]')
    parser.add_argument('-p', '--project_name', help='Project name')
    parser.add_argument('pdf_files', nargs='+', help='Positional arguments for paths to PDF files')
    args = parser.parse_args()
    combine_pdfs(args)


if __name__ == '__main__':
    main()
