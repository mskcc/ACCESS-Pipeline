#!/usr/bin/env cwl-runner

$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/
  doap: http://usefulinc.com/ns/doap#

$schemas:
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf
- http://usefulinc.com/ns/doap#

doap:release:
- class: doap:Version
  doap:name: module-3
  doap:revision: 1.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 1.0.0

dct:creator:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsoni@mskcc.org

dct:contributor:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsonsi@mskcc.org

cwlVersion: v1.0

class: Workflow
requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}


inputs:

  #########################
  # Marianas UMI Clipping #
  #########################

  # should be files! v
  fastq1: string
  fastq2: string
  sample_sheet: File
  umi_length: string
  output_project_folder: string
  outdir: string

  ############
  # Module 1 #
  ############

  adapter: string
  adapter2: string
  genome: string
#  bwa_output: string
  add_rg_LB: string
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string
  tmp_dir: string

  ###########
  # Fulcrum #
  ###########

  tmp_dir: string
  sort_order: string
  grouping_strategy: string
  min_mapping_quality: string
  tag_family_size_counts_output: string
  reference_fasta: File
  filter_min_reads: string
  filter_min_base_quality: string

  #########
  # Waltz #
  #########

  coverage_threshold: string
  gene_list: string
  bed_file: string
  min_mapping_quality: string
  waltz_reference_fasta: string
  waltz_reference_fasta_fai: string


outputs:

#  dir_out:
#    type: Directory
#    type: Directory
#    outputBinding:
#      glob: .

  # todo - should be an array?

  output_sample_sheet:
    type: File
    outputSource: cmo_process_loop_umi_fastq/output_sample_sheet

  # todo:
  # I don't understand how these can be arrays,
  # if this workflow is called with just a single pair of fastqs...
  standard_bams:
    type: File
    outputSource: module_1_innovation/bam

  fulcrum_bams:
    type: File
    outputSource: module_1_post_fulcrum/bam

  standard_waltz_files:
    type:
      type: array
      items: File
    outputSource: group_standard_waltz_files/waltz_files

#  marianas_waltz_files:
#    type:
#      type: array
#      items: File
#    outputSource: group_marianas_waltz_files/waltz_files

  fulcrum_waltz_files:
    type:
      type: array
      items: File
    outputSource: group_fulcrum_waltz_files/waltz_files


steps:

  #########################
  # Marianas UMI Clipping #
  #########################

  cmo_process_loop_umi_fastq:
    run: ./cmo-marianas.ProcessLoopUMIFastq/0.0.0/cmo-marianas.ProcessLoopUMIFastq.cwl
    in:
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      umi_length: umi_length
      # todo - doesnt need two outdirs
      output_project_folder: output_project_folder
    out: [processed_fastq_1, processed_fastq_2, info, output_sample_sheet, umi_frequencies]


  ####################
  # Adapted module 1 #
  ####################

  # todo - do we want adapter trimming here or not?
  module_1_innovation:
    run: ./module-1.innovation.cwl
    in:
      fastq1: cmo_process_loop_umi_fastq/processed_fastq_1
      fastq2: cmo_process_loop_umi_fastq/processed_fastq_2

      adapter: adapter
      adapter2: adapter2

      genome: genome
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      output_suffix:
        valueFrom: ${ return '_standard' }
    out:
      [bam, bai, md_metrics] # clstats1, clstats2,


  #############################
  # Waltz Run (Standard Bams) #
  #############################

  standard_waltz_count_reads:
    run: ./cmo-waltz.CountReads/0.0.0/cmo-waltz.CountReads.cwl
    in:
      input_bam: module_1_innovation/bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
    out: [
      covered_regions,
      fragment_sizes,
      read_counts
    ]

  standard_waltz_pileup_metrics:
    run: ./cmo-waltz.PileupMetrics/0.0.0/cmo-waltz.PileupMetrics.cwl
    in:
      input_bam: module_1_innovation/bam
      min_mapping_quality: min_mapping_quality
      reference_fasta: waltz_reference_fasta
      reference_fasta_fai: waltz_reference_fasta_fai
      bed_file: bed_file
    out: [
      pileup,
      pileup_without_duplicates,
      intervals,
      intervals_without_duplicates
    ]

  group_standard_waltz_files:
    run: ./innovation-group-waltz-files/innovation-group-waltz-files.cwl
    in:
      covered_regions: standard_waltz_count_reads/covered_regions
      fragment_sizes: standard_waltz_count_reads/fragment_sizes
      read_counts: standard_waltz_count_reads/read_counts
      pileup: standard_waltz_pileup_metrics/pileup
      pileup_without_duplicates: standard_waltz_pileup_metrics/pileup_without_duplicates
      intervals: standard_waltz_pileup_metrics/intervals
      intervals_without_duplicates: standard_waltz_pileup_metrics/intervals_without_duplicates
    out: [waltz_files]


  ###########################
  # Collapsing with Fulcrum #
  ###########################

  fulcrum:
    run: ./fulcrum_workflow.cwl
    in:
      tmp_dir: tmp_dir
      input_bam: module_1_innovation/bam
      sort_order: sort_order

      # Fulcrum group reads
      grouping_strategy: grouping_strategy
      min_mapping_quality: min_mapping_quality
      tag_family_size_counts_output: tag_family_size_counts_output

      # Fulcrum call duplex consensus reads
      reference_fasta: reference_fasta

      # Fulcrum filter reads
      filter_min_reads: filter_min_reads
      filter_min_base_quality: filter_min_base_quality

    out:
      [output_fastq_1, output_fastq_2]

  module_1_post_fulcrum:
    run: ./module-1.innovation.cwl
    in:
      # todo - adapter trimming again?
      fastq1: fulcrum/output_fastq_1
      fastq2: fulcrum/output_fastq_2
      adapter: adapter
      adapter2: adapter2
      genome: genome
#      bwa_output: bwa_output
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      output_suffix:
        valueFrom: ${ return '_fulcrum' }
    out:
      [bam, bai, md_metrics, clstats1, clstats2]

  #################################
  # Waltz Run (Fulcrum Collapsed) #
  #################################

  fulcrum_waltz_count_reads:
    run: ./cmo-waltz.CountReads/0.0.0/cmo-waltz.CountReads.cwl
    in:
      input_bam: module_1_post_fulcrum/bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
    out: [
      covered_regions,
      fragment_sizes,
      read_counts
    ]

  fulcrum_waltz_pileup_metrics:
    run: ./cmo-waltz.PileupMetrics/0.0.0/cmo-waltz.PileupMetrics.cwl
    in:
      input_bam: module_1_post_fulcrum/bam
      min_mapping_quality: min_mapping_quality
      reference_fasta: waltz_reference_fasta
      reference_fasta_fai: waltz_reference_fasta_fai
      bed_file: bed_file
    out: [
      pileup,
      pileup_without_duplicates,
      intervals,
      intervals_without_duplicates
    ]

  group_fulcrum_waltz_files:
    run: ./innovation-group-waltz-files/innovation-group-waltz-files.cwl
    in:
      covered_regions: fulcrum_waltz_count_reads/covered_regions
      fragment_sizes: fulcrum_waltz_count_reads/fragment_sizes
      read_counts: fulcrum_waltz_count_reads/read_counts
      pileup: fulcrum_waltz_pileup_metrics/pileup
      pileup_without_duplicates: fulcrum_waltz_pileup_metrics/pileup_without_duplicates
      intervals: fulcrum_waltz_pileup_metrics/intervals
      intervals_without_duplicates: fulcrum_waltz_pileup_metrics/intervals_without_duplicates
    out: [waltz_files]


  ############################
  # Collapsing with Marianas #
  ############################

#  marianas:
#    run: ./marianas_collapsing_workflow.cwl
#    in:
#      input_bam: module_1_innovation/bam
#      reference_fasta: reference_fasta
#      pileup: standard_waltz_pileup_metrics/pileup
#      mismatches: '1'
#      wobble: '2'
#    out:
#     [output_fastq_1, output_fastq_2]
#
#  module_1_post_marianas:
#    run: ./module-1.innovation.cwl
#    in:
#      # todo - adapter trimming again?
#      fastq1: marianas/output_fastq_1
#      fastq2: marianas/output_fastq_2
#      adapter: adapter
#      adapter2: adapter2
#      genome: genome
#      bwa_output: bwa_output
#      add_rg_LB: add_rg_LB
#      add_rg_PL: add_rg_PL
#      add_rg_ID: add_rg_ID
#      add_rg_PU: add_rg_PU
#      add_rg_SM: add_rg_SM
#      add_rg_CN: add_rg_CN
#      add_rg_output: add_rg_output
#      md_output: md_output
#      md_metrics_output: md_metrics_output
#      tmp_dir: tmp_dir
#      output_filename_suffix: '_marianas'
#    out:
#      [bam, bai, md_metrics, clstats1, clstats2]
#
#  ##################################
#  # Waltz Run (Marianas Collapsed) #
#  ##################################
#
#  marianas_waltz_count_reads:
#    run: ./cmo-waltz.CountReads/0.0.0/cmo-waltz.CountReads.cwl
#    in:
#      input_bam: module_1_post_marianas/bam
#      coverage_threshold: coverage_threshold
#      gene_list: gene_list
#      bed_file: bed_file
#    out: [
#      covered_regions,
#      fragment_sizes,
#      read_counts
#      ]
#
#  marianas_waltz_pileup_metrics:
#    run: ./cmo-waltz.PileupMetrics/0.0.0/cmo-waltz.PileupMetrics.cwl
#    in:
#      input_bam: module_1_post_marianas/bam
#      min_mapping_quality: min_mapping_quality
#      reference_fasta: waltz_reference_fasta
#      reference_fasta_fai: waltz_reference_fasta_fai
#      bed_file: bed_file
#    out: [
#      pileup,
#      pileup_without_duplicates,
#      intervals,
#      intervals_without_duplicates
#      ]
#
#  group_marianas_waltz_files:
#    run: ./innovation-group-waltz-files/innovation-group-waltz-files.cwl
#    in:
#      covered_regions: marianas_waltz_count_reads/covered_regions
#      fragment_sizes: marianas_waltz_count_reads/fragment_sizes
#      read_counts: marianas_waltz_count_reads/read_counts
#      pileup: marianas_waltz_pileup_metrics/pileup
#      pileup_without_duplicates: marianas_waltz_pileup_metrics/pileup_without_duplicates
#      intervals: marianas_waltz_pileup_metrics/intervals
#      intervals_without_duplicates: marianas_waltz_pileup_metrics/intervals_without_duplicates
#    out: [waltz_files]
