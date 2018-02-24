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
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 0.0.0

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

  # Marianas UMI Clipping
  fastq1: File
  fastq2: File
  sample_sheet: File
  umi_length: string
  output_project_folder: string
  outdir: string

  # Module 1
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

  # Fulcrum
  tmp_dir: string
  sort_order: string
  grouping_strategy: string
  min_mapping_quality: string
  tag_family_size_counts_output: string

  reference_fasta: string
  reference_fasta_fai: string

  # CallDuplexConsensusReads
  call_duplex_min_reads: string
  # FilterConsensusReads
  filter_min_reads: string
  filter_min_base_quality: string

  # Marianas
  marianas__mismatches: string
  marianas__wobble: string
  marianas__min_consensus_percent: string
  marianas_collapsing__outdir: string

  # Waltz
  coverage_threshold: string
  gene_list: string
  bed_file: File
  waltz__min_mapping_quality: string


outputs:

  # todo - should be an array?
  output_sample_sheet:
    type: File
    outputSource: process_loop_umi_fastq/output_sample_sheet

  duplex_seq_metrics:
    type: File
    outputSource: fulcrum/duplex_seq_metrics

  ####################
  # Output Bams (x5) #
  ####################

  # I don't understand how these can be arrays,
  # if this workflow is called with just a single pair of fastqs...
  #
  # Answer: CWL scatter step outputs are implicitly turned into arrays of the specified type
  standard_bams:
    type: File
    outputSource: module_1_innovation/bam

  fulcrum_simplex_duplex_bams:
    type: File
    outputSource: module_1_post_fulcrum_simplex_duplex/bam

  fulcrum_duplex_bams:
    type: File
    outputSource: module_1_post_fulcrum_duplex/bam

  marianas_simplex_duplex_bams:
    type: File
    outputSource: module_1_post_marianas_simplex_duplex/bam

  marianas_duplex_bams:
    type: File
    outputSource: module_1_post_marianas_duplex/bam

  #############################
  # Output Waltz Metrics (x5) #
  #############################

  standard_waltz_files:
    type:
      type: array
      items: File
    outputSource: waltz_standard/waltz_output_files

  fulcrum_simplex_duplex_waltz_files:
    type:
      type: array
      items: File
    outputSource: waltz_fulcrum_simplex_duplex/waltz_output_files

  fulcrum_duplex_waltz_files:
    type:
      type: array
      items: File
    outputSource: waltz_fulcrum_duplex/waltz_output_files

  marianas_simplex_duplex_waltz_files:
    type:
      type: array
      items: File
    outputSource: waltz_marianas_simplex_duplex/waltz_output_files

  marianas_duplex_waltz_files:
    type:
      type: array
      items: File
    outputSource: waltz_marianas_duplex/waltz_output_files

steps:

  #########################
  # Marianas UMI Clipping #
  #########################

  process_loop_umi_fastq:
    run: ../cwl_tools/marianas/ProcessLoopUMIFastq.cwl
    in:
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      umi_length: umi_length
      output_project_folder: output_project_folder
    out: [processed_fastq_1, processed_fastq_2, info, output_sample_sheet, umi_frequencies]

  ####################
  # Adapted module 1 #
  ####################

  # todo - do we want adapter trimming here or not?
  module_1_innovation:
    run: ./module-1.cwl
    in:
      fastq1: process_loop_umi_fastq/processed_fastq_1
      fastq2: process_loop_umi_fastq/processed_fastq_2

      adapter: adapter
      adapter2: adapter2

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

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

  waltz_standard:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: module_1_innovation/bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out:
      [pileup, waltz_output_files]

  ###########################
  # Collapsing with Fulcrum #
  ###########################

  fulcrum:
    run: ./fulcrum/fulcrum_workflow.cwl
    in:
      tmp_dir: tmp_dir
      input_bam: module_1_innovation/bam
      sort_order: sort_order

      # Fulcrum group reads
      grouping_strategy: grouping_strategy
      min_mapping_quality: min_mapping_quality
      tag_family_size_counts_output: tag_family_size_counts_output

      # Fulcrum call duplex consensus reads
      call_duplex_min_reads: call_duplex_min_reads

      # Fulcrum filter reads
      reference_fasta: reference_fasta
      filter_min_reads: filter_min_reads
      filter_min_base_quality: filter_min_base_quality

    out:
      [simplex_duplex_fastq_1, simplex_duplex_fastq_2, duplex_fastq_1, duplex_fastq_2, duplex_seq_metrics]

  module_1_post_fulcrum_simplex_duplex:
    run: ./module-1.cwl
    in:
      # todo - adapter trimming again?
      fastq1: fulcrum/simplex_duplex_fastq_1
      fastq2: fulcrum/simplex_duplex_fastq_2
      adapter: adapter
      adapter2: adapter2
      genome: genome
#      bwa_output: bwa_output
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      output_suffix:
        valueFrom: ${ return '_simplex_duplex' }
    out:
      [bam, bai, md_metrics, clstats1, clstats2]

  module_1_post_fulcrum_duplex:
    run: ./module-1.cwl
    in:
      # todo - adapter trimming again?
      fastq1: fulcrum/duplex_fastq_1
      fastq2: fulcrum/duplex_fastq_2
      adapter: adapter
      adapter2: adapter2
      genome: genome
#      bwa_output: bwa_output
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      output_suffix:
        valueFrom: ${ return '_duplex' }
    out:
      [bam, bai, md_metrics, clstats1, clstats2]

  #################################
  # Waltz Run (Fulcrum Collapsed) #
  #################################

  waltz_fulcrum_simplex_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: module_1_post_fulcrum_simplex_duplex/bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out:
      [pileup, waltz_output_files]

  waltz_fulcrum_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: module_1_post_fulcrum_duplex/bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out:
      [pileup, waltz_output_files]

  ############################
  # Collapsing with Marianas #
  ############################

  marianas_simplex_duplex:
    run: ./marianas/marianas_collapsing_workflow_simplex_duplex.cwl
    in:
      input_bam: module_1_innovation/bam
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      pileup: waltz_standard/pileup
      mismatches: marianas__mismatches
      wobble: marianas__wobble
      min_consensus_percent: marianas__min_consensus_percent

      output_dir: marianas_collapsing__outdir
    out:
     [output_fastq_1, output_fastq_2]

  module_1_post_marianas_simplex_duplex:
    run: ./module-1.cwl
    in:
      # todo - adapter trimming again?
      fastq1: marianas_simplex_duplex/output_fastq_1
      fastq2: marianas_simplex_duplex/output_fastq_2
      adapter: adapter
      adapter2: adapter2
      genome: genome
#      bwa_output: bwa_output
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      output_suffix:
        valueFrom: ${ return '_marianas_simplex_duplex' }
    out:
      [bam, bai, md_metrics, clstats1, clstats2]

  marianas_duplex:
    run: ./marianas/marianas_collapsing_workflow_duplex.cwl
    in:
      input_bam: module_1_innovation/bam
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      pileup: waltz_standard/pileup
      mismatches: marianas__mismatches
      wobble: marianas__wobble
      min_consensus_percent: marianas__min_consensus_percent

      output_dir: marianas_collapsing__outdir

    out:
     [output_fastq_1, output_fastq_2]

  module_1_post_marianas_duplex:
    run: ./module-1.cwl
    in:
      # todo - adapter trimming again?
      fastq1: marianas_duplex/output_fastq_1
      fastq2: marianas_duplex/output_fastq_2
      adapter: adapter
      adapter2: adapter2
      genome: genome
#      bwa_output: bwa_output
      add_rg_LB: add_rg_LB

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      output_suffix:
        valueFrom: ${ return '_marianas_duplex' }
    out:
      [bam, bai, md_metrics, clstats1, clstats2]

  ##################################
  # Waltz Run (Marianas Collapsed) #
  ##################################

  waltz_marianas_simplex_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: module_1_post_marianas_simplex_duplex/bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out:
      [pileup, waltz_output_files]

  waltz_marianas_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: module_1_post_marianas_duplex/bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out:
      [pileup, waltz_output_files]
