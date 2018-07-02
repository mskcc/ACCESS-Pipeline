import sys
from PyPDF2 import PdfFileMerger


FINAL_QC_FILENAME = 'main_qc.pdf'


def combine_pdfs():
    merger = PdfFileMerger()

    for pdf in sys.argv[1:]:
        print(pdf)

        merger.append(open(pdf), 'rb')

    with open('./' + FINAL_QC_FILENAME, 'wb') as fout:
        merger.write(fout)


def main():
    combine_pdfs()


if __name__ == '__main__':
    main()
