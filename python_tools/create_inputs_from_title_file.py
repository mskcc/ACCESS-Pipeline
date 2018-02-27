import os
import sys
import yaml
from glob import glob
import pandas as pd


title_file_path = sys.argv[1]
data_dir = sys.argv[2]

title_file = pd.read_csv(title_file_path, sep='\t')

fastq1 = [y for x in os.walk(data_dir) for y in glob(os.path.join(x[0], '*_R1_001.fastq.gz'))]
fastq1 = [{'class': 'File', 'path': x} for x in fastq1]

fastq2 = [y for x in os.walk(data_dir) for y in glob(os.path.join(x[0], '*_R2_001.fastq.gz'))]
fastq2 = [{'class': 'File', 'path': x} for x in fastq2]

sample_sheet = [y for x in os.walk(data_dir) for y in glob(os.path.join(x[0], 'SampleSheet.csv'))]
sample_sheet = [{'class': 'File', 'path': x} for x in sample_sheet]

out = open('inputs.yaml', 'wb')

# GATCGGAAGAGCACACGTCTGAACTCCAGTCAC + bc_1 + ATATCTCGTATGCCGTCTTCTGCTTG
adapter = 'GATCGGAAGAGCACACGTCTGAACTCCAGTCAC'
adapter += title_file['barcode_index_1'].astype(str)
adapter += 'ATATCTCGTATGCCGTCTTCTGCTTG'

# AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT + bc_2 + AGATCTCGGTGGTCGCCGTATCATT
adapter2 = 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'
adapter2 += title_file['barcode_index_2'].astype(str)
adapter2 += 'AGATCTCGGTGGTCGCCGTATCATT'

out_dict = {
    'fastq1': fastq1,
    'fastq2': fastq2,
    'sample_sheet': sample_sheet,

    'adapter': adapter.tolist(),
    'adapter2': adapter2.tolist(),

    # Todo: what's the difference between ID & SM?
    'add_rg_ID': title_file['Sample_ID'].tolist(),
    'add_rg_SM': title_file['Sample_ID'].tolist(),
    'add_rg_LB': title_file['Lane'].tolist(),

    # Todo: should use one or two barcodes if they are different?
    'add_rg_PU': title_file['barcode_index_1'].tolist(),
}



other_params = {
    'title_file': {'class': 'File', 'path': title_file_path},
    'bed_file': {'class': 'File', 'path': '../resources/pan-cancer-panel.sorted.bed'},

    'reference_fasta': '/ifs/depot/resources/dmp/data/pubdata/hg-fasta/VERSIONS/hg19/Homo_sapiens_assembly19.fasta',
    'reference_fasta_fai': '/ifs/depot/resources/dmp/data/pubdata/hg-fasta/VERSIONS/hg19/Homo_sapiens_assembly19.fasta.fai',

    ##########################
    # Process Loop UMI Fastq #
    ##########################

    'umi_length': '3',
    'output_project_folder': '.',

    ##############
    # TrimGalore #
    ##############

    'genome': 'GRCh37',

    ###########################
    # AddOrReplcaceReadGroups #
    ###########################

    'add_rg_PL': 'Illumina',
    # Todo: Should say: add_rg_CN: "InnovationLab"?
    'add_rg_CN': 'BergerLab_MSKCC',

    ######################
    # FixMateInformation #
    ######################

    'fix_mate_information__sort_order': 'coordinate',
    'fix_mate_information__validation_stringency': 'LENIENT',
    'fix_mate_information__compression_level': '0',
    'fix_mate_information__create_index': 'true',

    ########
    # Abra #
    ########

    'abra__kmers': '43 53 63 83 93',

    ###########
    # Fulcrum #
    ###########

    'tmp_dir': '/scratch',
    # SortBam
    'sort_order': 'Queryname',
    # GroupReadsByUMI
    'grouping_strategy': 'paired',
    'min_mapping_quality': '20',
    'tag_family_size_counts_output': 'Grouped-mapQ20-histogram',
    # CallDuplexConsensusReads
    'call_duplex_min_reads': '1 1 0',
    # FilterConsensusReads
    'filter_min_reads': '2 1 0',
    'filter_min_base_quality': '30',

    ############
    # Marianas #
    ############

    'marianas__mismatches': '1',
    'marianas__wobble': '3',
    'marianas__min_consensus_percent': '90',
    'marianas_collapsing__outdir': '.',

    #########
    # Waltz #
    #########

    'coverage_threshold': '20',
    'gene_list': '../resources/juber-hg19-gene-list.bed',
    'waltz__min_mapping_quality': '20',
}

out.write(yaml.dump(other_params))
out.write(yaml.dump(out_dict))
out.close()
