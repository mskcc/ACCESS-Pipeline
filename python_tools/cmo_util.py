import os
import re
import sys
import magic
import logging
import subprocess
import ruamel.yaml
from python_tools.constants import ACCESS_VARIANTS_RUN_TOOLS_PATH

# Set up logging
FORMAT = '%(asctime)-15s %(funcName)-8s %(levelname)s %(message)s'
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter(FORMAT))
out_hdlr.setLevel(logging.INFO)
logger = logging.getLogger('cmo_util')
logger.addHandler(out_hdlr)
logger.setLevel(logging.DEBUG)


# Get tools from configuration
# Todo: Containerize
with open(ACCESS_VARIANTS_RUN_TOOLS_PATH, 'r') as stream:
    tools_config = ruamel.yaml.round_trip_load(stream)

    try:
        TABIX_LOCATION, BGZIP_LOCATION, SORTBED_LOCATION, BCFTOOLS_LOCATION_1_6 = \
            map(lambda x: tools_config['run_tools'][x],
                ('tabix', 'bgzip', 'sortbed', 'bcftools_1_6'))
    except KeyError as e:
        raise Exception(
            "{} path is not defined in yaml config file.".format(e))

# TABIX_LOCATION = '/dmp/resources/prod/tools/bio/htslib/VERSIONS/htslib-1.3.2/tabix'
# BGZIP_LOCATION = '/dmp/resources/prod/tools/bio/htslib/VERSIONS/htslib-1.3.2/bgzip'
# SORTBED_LOCATION = '/dmp/resources/prod/tools/bio/bedtools/VERSIONS/bedtools-2.27.1/bin/sortBed'
# BCFTOOLS_LOCATION_1_6 = '/dmp/resources/prod/tools/bio/bcftools/VERSIONS/bcftools-1.3.1/bcftools'


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


def bgzip_decompress(vcf):
    """
    Decompresses a gzipped VCF file

    :param vcf: str - VCF file name
    :return:
    """
    if not re.search(r'.gz$', vcf):
        logging.error('non-compressed file %s passed to bgzip_decompress' %vcf)
        raise ValueError

    # Need to write the final file to current step's working directory so that CWL runner can find it
    basename = os.path.basename(vcf)
    outfile = basename.replace('.vcf.gz', '.vcf')
    cmd = [BGZIP_LOCATION, '-d', '-c', '-f', vcf]
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
    process_one = subprocess.Popen([BCFTOOLS_LOCATION_1_6, 'view', '%s' % (vcf_file)], stdout=subprocess.PIPE)
    vcf = re.sub(r'(?P<id>##contig=<ID=[^>]+)', r'\1,length=0', process_one.communicate()[0])
    process_two = subprocess.Popen([BGZIP_LOCATION, '-c'], stdin=subprocess.PIPE, stdout=open(vcf_file, 'w'))
    process_two.communicate(input=vcf)


def fix_contig_tag_in_vcf_by_line(vcf_file):
    """
    Appears to add a "length=0" tag to the header of the VCF?

    :param vcf_file:
    :return:
    """
    cmd_array = [BCFTOOLS_LOCATION_1_6, 'view', '%s' % (vcf_file)]
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
        BCFTOOLS_LOCATION_1_6, 'norm',
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


def annotate_vcf(combined_vcf, anno_with_vcf, tmp_header):
    """
    Use bcftools to annotate combined vcf with mutect

    :param combined_vcf:
    :param anno_with_vcf:
    :param tmp_header
    :return:
    """
    output_vcf = combined_vcf.replace('.vcf.gz', '_anno.vcf.gz')

    cmd = [
        BCFTOOLS_LOCATION_1_6, 'annotate',
        '--annotations', anno_with_vcf,
        '--header-lines', tmp_header,
        '--mark-sites', '+MUTECT',
        '--output-type', 'z',
        '--output', output_vcf,
        combined_vcf
    ]

    logger.debug('bcftools annotate Command: %s' % (' '.join(cmd)))
    subprocess.check_call(cmd)
    # fix_contig_tag_in_vcf_by_line(output_vcf)
    # fix_contig_tag_in_vcf(output_vcf)

    os.unlink(combined_vcf)
    os.unlink('%s.tbi' % (combined_vcf))
    return output_vcf
