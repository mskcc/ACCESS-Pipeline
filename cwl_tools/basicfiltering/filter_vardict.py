#! python

"""
@Description : This tool helps to filter vardict version 1.4.6 vcf
@Created : 04/22/2016
@Updated : 03/26/2018
@Updated : 01/xx/2019
@author : Ronak H Shah, Cyriac Kandoth, Ian Johnson


Visual representation of how this module works:

"Somatic" not in record['STATUS'] and args.filter_germline ?
|
yes --> DONT KEEP
|
no --> tumor_variant_fraction > nvfRF ?
        |
        no --> DONT KEEP
        |
        yes --> tmq >= args.mq and
                nmq >= args.mq and
                tdp >= args.dp and
                tad >= args.ad and
                tvf >= args.vf ?
                |
                no --> DONT KEEP
                |
                yes --> KEEP

Note: BasicFiltering VarDict's additional filters over MuTect include:
1. Tumor variant quality threshold
2. Normal variant quality threshold
3. Somatic filter (MuTect does not report germline events)
"""

from __future__ import division

import os
import sys
import vcf
import gzip
import time
import logging
import argparse

from vcf.parser import _Info as VcfInfo, _Format as VcfFormat

from python_tools import cmo_util


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)

logger = logging.getLogger('filter_vardict')


def main():
    parser = argparse.ArgumentParser(prog='filter_vardict.py',description='Filter snps/indels from the output of vardict v1.4.6',usage='%(prog)s [options]')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',help="make lots of noise")
    parser.add_argument('-ivcf', '--inputVcf', action='store', dest='inputVcf', required=True, type=str, metavar='SomeID.vcf',help="Input vcf vardict file which needs to be filtered")
    parser.add_argument('-tsn', '--tsampleName', action='store', dest='tsampleName', required=True, type=str, metavar='SomeName',help="Name of the tumor Sample")
    parser.add_argument('-rf', '--refFasta', action='store', dest='refFasta', required=True, type=str, metavar='ref.fa', help="Reference genome in fasta format")
    parser.add_argument('-dp', '--totaldepth', action='store', dest='dp', required=True, type=int, metavar='5',help="Tumor total depth threshold")
    parser.add_argument('-ad', '--alleledepth', action='store', dest='ad', required=True, type=int, metavar='3',help="Tumor allele depth threshold")
    parser.add_argument('-tnr', '--tnRatio', action='store', dest='tnr', required=True, type=int, metavar='5',help="Tumor-Normal variant fraction ratio threshold")
    parser.add_argument('-vf', '--variantfraction', action='store', dest='vf', required=True, type=float, metavar='0.01',help="Tumor variant fraction threshold")
    parser.add_argument('-mq', '--minqual', action='store', dest='mq', required=True, type=int, metavar='20',help="Minimum variant call quality")
    parser.add_argument('-fg', '--filter_germline', action='store', dest='filter_germline', type=bool, help="Whether to remove calls without 'somatic' status")
    parser.add_argument('-o', '--outDir', action='store', dest='outdir', required=False, type=str, metavar='/somepath/output',help="Full Path to the output dir.")
    args = parser.parse_args()

    if args.verbose:
        logger.info("Started the run for doing standard filter.")

    run_std_filter(args)

    if args.verbose:
        logger.info("Finished the run for doing standard filter.")


def run_std_filter(args):
    vcf_out = os.path.basename(args.inputVcf)
    vcf_out = os.path.splitext(vcf_out)[0]

    if args.outdir:
        vcf_out = os.path.join(args.outdir,vcf_out)

    txt_out = vcf_out + '_STDfilter.txt'
    vcf_complex_out = vcf_out + '_complex_STDfilter.vcf'
    vcf_out = vcf_out + '_STDfilter.vcf'

    vcf_reader = vcf.Reader(open(args.inputVcf, 'r'))
    vcf_reader.infos['set'] = VcfInfo('set', '.', 'String', 'The variant callers that reported this event', 'mskcc/basicfiltering', 'v0.2.1')
    vcf_reader.formats['DP'] = VcfFormat('DP', '1', 'Integer', 'Total read depth at this site')
    vcf_reader.formats['AD'] = VcfFormat('AD', 'R', 'Integer', 'Allelic depths for the ref and alt alleles in the order listed')

    allsamples = list(vcf_reader.samples)

    if len(allsamples) != 2:
        if args.verbose:
            logger.critical('The VCF does not have two genotype columns. Please input a proper vcf with Tumor/Normal columns')
        sys.exit(1)

    # If the caller reported the normal genotype column before the tumor, swap those around
    if_swap_sample = False
    if allsamples[1] == args.tsampleName:
        if_swap_sample = True
        vcf_reader.samples[0] = allsamples[1]
        vcf_reader.samples[1] = allsamples[0]

    nsampleName = vcf_reader.samples[1]

    vcf_writer = vcf.Writer(open(vcf_out, 'w'), vcf_reader)
    vcf_complex_writer = vcf.Writer(open(vcf_complex_out, 'w'), vcf_reader)
    txt_fh = open(txt_out, "wb")
    # Iterate through rows and filter mutations
    for record in vcf_reader:
        tcall = record.genotype(args.tsampleName)

        # Pad complex indels for proper genotyping
        if (record.INFO["TYPE"] == "Complex" and 
                len(record.REF) != len(record.ALT) and 
                record.INFO["SHIFT3"] > 0 and 
                record.INFO["SHIFT3"] <= len(record.INFO["LSEQ"])):
            padding_seq = record.INFO["LSEQ"][len(record.INFO["LSEQ"])-(record.INFO["SHIFT3"]+1):]
            record.REF = padding_seq + record.REF
            for alt in record.ALT:
                alt.sequence = padding_seq + alt.sequence
            record.POS = record.POS - (record.INFO["SHIFT3"]+1)
            # TODO: add ID=SHIFT3_ADJUSTED to vcf header
            record.INFO["SHIFT3_ADJUSTED"] = record.INFO["SHIFT3"]
            record.INFO["SHIFT3"] = 0
            complex_flag = True
        else:
            complex_flag = False
            record.INFO["SHIFT3_ADJUSTED"] = 0

        keep_based_on_status = True
        if "Somatic" not in record.INFO['STATUS'] and args.filter_germline:
            keep_based_on_status = False

        if tcall['QUAL'] is not None:
            tmq = int(tcall['QUAL'])
        else:
            tmq = 0
        if tcall['DP'] is not None:
            tdp = int(tcall['DP'])
        else:
            tdp = 0
        if tcall['VD'] is not None:
            tad = int(tcall['VD'])
        else:
            tad = 0
        if tdp != 0:
            tvf = int(tad) / float(tdp)
        else:
            tvf = 0

        ncall = record.genotype(nsampleName)
        if ncall:
            if ncall['QUAL'] is not None:
                nmq = int(ncall['QUAL'])
            else:
                nmq = 0
            if ncall['DP'] is not None:
                ndp = int(ncall['DP'])
            else:
                ndp = 0
            if ncall['VD'] is not None:
                nad = int(ncall['VD'])
            else:
                nad = 0
            if ndp != 0:
                nvf = nad / ndp
            else:
                nvf = 0
            nvfRF = int(args.tnr) * nvf
        else:
            logger.critical("filter_vardict: There are no genotype values for Normal. We will exit.")
            sys.exit(1)

        record.add_info('set', 'VarDict')

        if if_swap_sample:
            nrm = record.samples[0]
            tum = record.samples[1]
            record.samples[0] = tum
            record.samples[1] = nrm

        if tvf > nvfRF:
            if keep_based_on_status & (tmq >= int(args.mq)) & (nmq >= int(args.mq)) & (tdp >= int(args.dp)) & (tad >= int(args.ad)) & (tvf >= float(args.vf)):
                if complex_flag:
                    vcf_complex_writer.write_record(record)
                else:
                    vcf_writer.write_record(record)
                out_line = str.encode(args.tsampleName + "\t" + record.CHROM + "\t" + str(record.POS) + "\t" + str(record.REF) + "\t" + str(record.ALT[0]) + "\t" + "." + "\n")
                txt_fh.write(out_line)

    vcf_writer.close()
    vcf_complex_writer.close()
    txt_fh.close()

    # Normalize the non-complex events in the VCF, produce a bgzipped VCF, then tabix index it
    norm_gz_vcf = cmo_util.normalize_vcf(vcf_out, args.refFasta)
    merged_vcf = merge_sort_bgzip_vcf(norm_gz_vcf, vcf_complex_out)
    cmo_util.tabix_file(merged_vcf)


def merge_sort_bgzip_vcf(bgzip_vcf, vcf):
    with gzip.open(bgzip_vcf, 'a') as wvcf, open(vcf, 'r') as rvcf:
        for line in rvcf:
            if line.startswith("#"):
                continue
            wvcf.write(line)

    cmo_util.sort_vcf(bgzip_vcf)
    cmo_util.bgzip(bgzip_vcf, force=True)
    return(bgzip_vcf)

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    totaltime = end_time - start_time
    logging.info("filter_vardict: Elapsed time was %g seconds", totaltime)
    sys.exit(0)
