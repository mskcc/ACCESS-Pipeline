#! python

"""
@Description : 
@Created : 02/28/2019
@author : Maysun Hasan

"""

from __future__ import division

import os
import sys
import vcf
import time
import logging
import argparse
import pandas as pd

from vcf.parser import _Info as VcfInfo, _Format as VcfFormat

import cwl_tools.concatVCF.concat_util

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)

logger = logging.getLogger('anno_concat')


def parse_arguments():
    #TODO
    parser = argparse.ArgumentParser(prog='annotate_concat.py', description='Annotates the common variants in the combined vcf and another vcf with an additional column', usage='%(prog)s [options]')
    parser.add_argument('-ivcf', '--combined_vcf', required=True, type=str, help='Combined Input vcf that gets annotated')
    parser.add_argument('-avcf', '--anno_with_vcf', required=True, type=str, help='Input vcf to annoted with')
    parser.add_argument('-itxt', '--anno_header', required=True, type=str, help='Input txt header file')
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    logger.info('Started the run for annotating concated vcf.')
    final_file_path = annotate_concat_vcf(args)
    logger.info('Finished the run for annotating concatenated vcf: {}'.format(final_file_path))


def annotate_concat_vcf(args):
    # Normalize the events in the VCF, produce a bgzipped VCF, then tabix index it
    combined_gz_vcf = cwl_tools.concatVCF.concat_util.bgzip(args.combined_vcf)
    cwl_tools.concatVCF.concat_util.tabix_file(combined_gz_vcf)
    annotated_concat_gz_vcf = cwl_tools.concatVCF.concat_util.annotate_vcf(combined_gz_vcf, args.anno_with_vcf, args.anno_header)
    annotated_concat_vcf = cwl_tools.concatVCF.concat_util.bgzip_decompress(annotated_concat_gz_vcf)

    return annotated_concat_vcf


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    totaltime = end_time - start_time
    logging.info("annotate concat: Elapsed time was %g seconds", totaltime)
    sys.exit(0)
