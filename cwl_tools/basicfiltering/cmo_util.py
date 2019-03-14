import os
import re
import sys
import magic
import logging
import subprocess


# Todo: Move this file to top level util module

# Set up logging
FORMAT = '%(asctime)-15s %(funcName)-8s %(levelname)s %(message)s'
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter(FORMAT))
out_hdlr.setLevel(logging.INFO)
logger = logging.getLogger('cmo_util')
logger.addHandler(out_hdlr)
logger.setLevel(logging.DEBUG)


# Todo: Containerize
TABIX_LOCATION = '/opt/common/CentOS_6-dev/htslib/v1.3.2/tabix'
BGZIP_LOCATION = '/opt/common/CentOS_6-dev/htslib/v1.3.2/bgzip'
SORTBED_LOCATION = '/opt/common/CentOS_6-dev/bedtools/bedtools-2.26.0/bin/sortBed'
BCFTOOLS_LOCATION = '/opt/common/CentOS_6-dev/bcftools/bcftools-1.3.1/bcftools'


def sort_vcf(vcf):
    """
    Sort the VCF file, and add .sorted extension

    :param vcf: VCF file path
    """
    outfile = vcf.replace('.vcf', '.sorted.vcf')

    cmd = [SORTBED_LOCATION, '-i', vcf, '-header']
    subprocess.check_call(cmd, stdout=open(outfile, 'w'))

    cmd = ['mv', outfile, vcf]
    subprocess.call(cmd)


def bgzip(vcf):
    """
    gzip a VCF file

    :param vcf: str VCF file path
    :return:
    """
    if re.search(r'.gz$', vcf):
        return vcf

    outfile = '%s.gz' % (vcf)
    cmd = [BGZIP_LOCATION, '-c', vcf]
    subprocess.call(cmd, stdout=open(outfile, 'w'))
    return outfile


def tabix_file(vcf_file):
    """
    Index a vcf file with tabix for random access

    :param vcf_file: str - VCF file name
    """
    with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
        if (m.id_filename(vcf_file).find('gz') == -1):
            logger.critical(
                'VCF File needs to be bgzipped for tabix random access. tabix-0.26/bgzip should be compiled for use')
            sys.exit(1)

    cmd = [TABIX_LOCATION, '-p', 'vcf', vcf_file]
    logger.debug('Tabix command: %s' % (' '.join(cmd)))
    subprocess.check_call(cmd)


def fix_contig_tag_in_vcf(vcf_file):
    """
    Works for small files only

    :param vcf_file: str Path to VCF file
    :return:
    """
    process_one = subprocess.Popen([BCFTOOLS_LOCATION, 'view', '%s' % (vcf_file)], stdout=subprocess.PIPE)
    vcf = re.sub(r'(?P<id>##contig=<ID=[^>]+)', r'\1,length=0', process_one.communicate()[0])
    process_two = subprocess.Popen([BGZIP_LOCATION, '-c'], stdin=subprocess.PIPE, stdout=open(vcf_file, 'w'))
    process_two.communicate(input=vcf)


def fix_contig_tag_in_vcf_by_line(vcf_file):
    """
    Appears to add a contig "length=0" tag to the header of the VCF

    :param vcf_file:
    :return:
    """
    cmd_array = [BCFTOOLS_LOCATION, 'view', '%s' % (vcf_file)]
    process_one = subprocess.Popen(cmd_array, stdout=subprocess.PIPE)
    process_two = subprocess.Popen([BGZIP_LOCATION, '-c'], stdin=subprocess.PIPE, stdout=open('fixed.vcf', 'w'))

    with process_one.stdout as p:
        for line in iter(p.readline, ''):
            line = re.sub(r'(?P<id>##contig=<ID=[^>]+)', r'\1,length=0', line)
            process_two.stdin.write('%s\n' % (line))

    process_two.stdin.close()
    process_two.wait()

    # Rename fixed file
    cmd = ['mv', 'fixed.vcf', vcf_file]
    subprocess.call(cmd)


def normalize_vcf(vcf_file, ref_fasta):
    """
    Use bcftools for VCF normalization

    :param vcf_file: str Path to VCF file
    :param ref_fasta: str Path to reference fasta file
    :return:
    """
    output_vcf = vcf_file.replace('.vcf', '.norm.vcf.gz')
    # sort_vcf(vcf_file)
    vcf_gz_file = bgzip(vcf_file)
    tabix_file(vcf_gz_file)

    cmd = [
        BCFTOOLS_LOCATION, 'norm',
        '--check-ref', 's',
        '--fasta-ref', ref_fasta,
        '--multiallelics', '+any',
        '--output-type', 'z',
        '--output', output_vcf,
        vcf_gz_file
    ]

    logger.debug('bcftools norm Command: %s' % (' '.join(cmd)))
    subprocess.check_call(cmd)
    # fix_contig_tag_in_vcf_by_line(output_vcf)
    # fix_contig_tag_in_vcf(output_vcf)

    os.unlink(vcf_gz_file)
    os.unlink('%s.tbi' % (vcf_gz_file))
    return output_vcf
