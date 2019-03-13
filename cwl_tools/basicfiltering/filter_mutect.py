#! python

"""
@Description : This tool helps to filter muTect v1.1.4 txt and vcf
@Created : 07/17/2016
@Updated : 03/26/2018
@Updated : 01/xx/2019
@author : Ronak H Shah, Cyriac Kandoth, Ian Johnson


Visual representation of how this module works:

judgement == 'KEEP' ?
|
no --> any([not (t in ACCEPTED_TAGS) for t in failure_reason_tags]) ?
        |
        yes --> DONT KEEP
        |
        no -->  go to (2)
|
yes --> (2) tumor_variant_fraction > (normal_variant_fraction * args.tumor_normal_ratio) ?
        |
        no --> DONT KEEP
        |
        yes --> tumor_depth >= args.dp and
                tumor_alt_dept >= args.ad and
                tumor_variant_fraction >= args.vf ?
                |
                yes --> KEEP
                |
                no --> DONT KEEP

Note: BasicFiltering MuTect's additional filters over VarDict include:
1. Logic for filtering based on failure reasons
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

import cwl_tools.basicfiltering.cmo_util

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)

logger = logging.getLogger('filter_mutect')

# Variants with ONLY these tags in their failure_reason column should still be considered to pass
# Todo: waiting for comprehensive list from Gowtham
ACCEPTED_TAGS = [
    'alt_allele_in_normal',
    'clustered_read_position',
    # Todo: should have underscore?
    # 'DBSNP Site',
    'fstar_tumor_lod',
    'nearby_gap_events',
    'normal_lod',
    'poor_mapping_region_alternate_allele_mapq',
    'possible_contamination',
    'strand_artifact',
    'triallelic_site',
]


def main():
    parser = argparse.ArgumentParser(prog='filter_mutect.py', description='Filter snps from the output of muTect v1.1.4', usage='%(prog)s [options]')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='make lots of noise')
    parser.add_argument('-ivcf', '--inputVcf', action='store', dest='inputVcf', required=True, type=str, metavar='SomeID.vcf', help='Input vcf muTect file which needs to be filtered')
    parser.add_argument('-itxt', '--inputTxt', action='store', dest='inputTxt', required=True, type=str, metavar='SomeID.txt', help='Input txt muTect file which needs to be filtered')
    parser.add_argument('-tsn', '--tsampleName', action='store', dest='tsampleName', required=True, type=str, metavar='SomeName', help='Name of the tumor Sample')
    parser.add_argument('-rf', '--refFasta', action='store', dest='refFasta', required=True, type=str, metavar='ref.fa', help='Reference genome in fasta format')
    parser.add_argument('-dp', '--totaldepth', action='store', dest='dp', required=False, type=int, default=5, metavar='5', help='Tumor total depth threshold')
    parser.add_argument('-ad', '--alleledepth', action='store', dest='ad', required=False, type=int, default=3, metavar='3', help='Tumor allele depth threshold')
    parser.add_argument('-tnr', '--tnRatio', action='store', dest='tnr', required=False, type=int, default=5, metavar='5', help='Tumor-Normal variant fraction ratio threshold')
    parser.add_argument('-vf', '--variantfraction', action='store', dest='vf', required=False, type=float, default=0.01, metavar='0.01', help='Tumor variant fraction threshold')
    parser.add_argument('-o', '--outDir', action='store', dest='outdir', required=False, type=str, metavar='/somepath/output', help='Full Path to the output dir.')
    args = parser.parse_args()

    logger.info('Started the run for doing standard filter.')
    run_std_filter(args)
    logger.info('Finished the run for doing standard filter.')


def run_std_filter(args):
    vcf_out = os.path.basename(args.inputVcf)
    vcf_out = os.path.splitext(vcf_out)[0]
    txt_out = os.path.basename(args.inputTxt)
    txt_out = os.path.splitext(txt_out)[0]

    if args.outdir:
        vcf_out = os.path.join(args.outdir, vcf_out)
        txt_out = os.path.join(args.outdir, txt_out)

    vcf_out = vcf_out + '_STDfilter.vcf'
    txt_out = txt_out + '_STDfilter.txt'
    vcf_reader = vcf.Reader(open(args.inputVcf, 'r'))
    vcf_reader.infos['FAILURE_REASON'] = VcfInfo('FAILURE_REASON', '.', 'String', 'Failure Reason from MuTect text File', 'muTect', 'v1.1.5')
    vcf_reader.infos['set'] = VcfInfo('set', '.', 'String', 'The variant callers that reported this event', 'mskcc/basicfiltering', 'v0.2.1')
    vcf_reader.formats['DP'] = VcfFormat('DP', '1', 'Integer', 'Total read depth at this site')
    vcf_reader.formats['AD'] = VcfFormat('AD', 'R', 'Integer', 'Allelic depths for the ref and alt alleles in the order listed')

    allsamples = list(vcf_reader.samples)
    if len(allsamples) != 2:
        logger.critical("The VCF does not have two genotype columns. Please input a proper vcf with Tumor/Normal columns")
        sys.exit(1)

    # If the caller reported the normal genotype column before the tumor, swap those around
    if_swap_sample = False
    if allsamples[1] == args.tsampleName:
        if_swap_sample = True
        vcf_reader.samples[0] = allsamples[1]
        vcf_reader.samples[1] = allsamples[0]

    # Dictionary to store records to keep
    keepDict = {}


    # Filter each row (Mutation)
    txtDF = pd.read_table(args.inputTxt, skiprows=1, dtype=str)
    txt_fh = open(txt_out, "wb")
    for index, row in txtDF.iterrows():
        chr = row.loc['contig']
        pos = row.loc['position']
        ref_allele = row.loc['ref_allele']
        alt_allele = row.loc['alt_allele']
        trd = int(row.loc['t_ref_count'])
        tad = int(row.loc['t_alt_count'])

        ##############################
        # Tumor Variant Calculations #
        ##############################

        # Total Depth
        # Todo: Does this include indels? soft clipping?
        tdp = trd + tad

        # Variant Fraction
        if tdp != 0:
            tvf = int(tad) / float(tdp)
        else:
            tvf = 0

        ###############################
        # Normal Variant Calculations #
        ###############################

        nrd = int(row.loc['n_ref_count'])
        nad = int(row.loc['n_alt_count'])

        # Total Depth
        ndp = nrd + nad

        # Variant Fraction
        if ndp != 0:
            nvf = int(nad) / float(ndp)
        else:
            nvf = 0

        # Get REJECT or PASS
        judgement = row.loc['judgement']
        failure_reason = row.loc['failure_reasons']

        # nvfRF is one of the thresholds that the tumor variant fraction must exceed
        # in order to pass filtering.
        #
        # This threshold is equal to the normal variant fraction, multiplied by
        # the number of times greater we must see the mutation in the tumor (args.tnr):
        nvfRF = int(args.tnr) * nvf

        # This will help in filtering VCF
        key_for_tracking = str(chr) + ':' + str(pos) + ':' + str(ref_allele) + ':' + str(alt_allele)
        locus = str(chr) + ':' + str(pos)

        if judgement != 'KEEP':
            # Check the failure reasons to determine if we should still consider this variant
            failure_tags = failure_reason.split(',')
            tag_count = 0
            for tag in failure_tags:
                if tag in ACCEPTED_TAGS:
                    tag_count += 1
            # All failure_reasons should be found in accepted tags to continue
            if tag_count != len(failure_tags):
                continue
        else:
            failure_reason = 'KEEP'

        if tvf > nvfRF:
            if (tdp >= int(args.dp)) & (tad >= int(args.ad)) & (tvf >= float(args.vf)):
                if key_for_tracking in keepDict:
                    print('MutectStdFilter: There is a repeat ', key_for_tracking)
                else:
                    keepDict[key_for_tracking] = failure_reason
                txt_fh.write(args.tsampleName + "\t" + str(chr) + "\t" + str(pos) + "\t" + str(ref_allele) + "\t" + str(alt_allele) + "\t" + str(failure_reason) + "\n")

    txt_fh.close()

    # This section uses the keepDict to write all passed mutations to the new VCF file
    vcf_writer = vcf.Writer(open(vcf_out, 'w'), vcf_reader)
    for record in vcf_reader:
        key_for_tracking = str(record.CHROM) + ':' + str(record.POS) + ':' + str(record.REF) + ':' + str(record.ALT[0])

        if key_for_tracking in keepDict:
            failure_reason = keepDict.get(key_for_tracking)
            # There was no failure reason for calls that had "KEEP" in their judgement column,
            # but this code uses "KEEP" as the key when they are encountered
            if failure_reason == 'KEEP':
                failure_reason = 'None'

            record.add_info('FAILURE_REASON', failure_reason)
            record.add_info('set', 'MuTect')
            if if_swap_sample:
                nrm = record.samples[0]
                tum = record.samples[1]
                record.samples[0] = tum
                record.samples[1] = nrm

            if record.FILTER == 'PASS':
                vcf_writer.write_record(record)

            # Change the failure reason to PASS, for mutations for which we want to override MuTect's assessment
            else:
                record.FILTER = 'PASS'
                vcf_writer.write_record(record)
        else:
            continue

    vcf_writer.close()

    # Normalize the events in the VCF, produce a bgzipped VCF, then tabix index it
    norm_gz_vcf = cwl_tools.basicfiltering.cmo_util.normalize_vcf(vcf_out, args.refFasta)
    cwl_tools.basicfiltering.cmo_util.tabix_file(norm_gz_vcf)

    return norm_gz_vcf


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    totaltime = end_time - start_time
    logging.info("filter_mutect: Elapsed time was %g seconds", totaltime)
    sys.exit(0)
