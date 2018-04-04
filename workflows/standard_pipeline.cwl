#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

doc: |
  This is a workflow to go from UMI-tagged fastqs to standard bams.
  It does not include collapsing, or QC
  It does include modules 1 and 2

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:

  tmp_dir: string

  fastq1: File[]
  fastq2: File[]
  sample_sheet: File[]
  patient_id: string[]
  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file,
  # so we need to use strings here instead of file types
  reference_fasta: string
  reference_fasta_fai: string

  # Marianas Clipping
  umi_length: int
  output_project_folder: string
  # Module 1
  adapter: string[]
  adapter2: string[]
  add_rg_PL: string
  add_rg_CN: string
  add_rg_LB: int[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]
  md__create_index: boolean
  md__assume_sorted: boolean
  md__compression_level: int
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string
  # Module 2
  fci__minbq: int
  fci__minmq: int
  fci__cov: int
  fci__rf: string
  fci__intervals: string[]
  abra__kmers: string
  abra__scratch: string
  abra__mad: int
  fix_mate_information__sort_order: string
  fix_mate_information__create_index: boolean
  fix_mate_information__compression_level: int
  fix_mate_information__validation_stringency: string
  bqsr__nct: int
  bqsr__knownSites_dbSNP: File
  bqsr__knownSites_millis: File
  bqsr__rf: string
  print_reads__nct: int
  print_reads__EOQ: boolean
  print_reads__baq: string

outputs:

  standard_bams:
    type:
      type: array
      items: File
    outputSource: flatten_array_bams/output_bams

steps:

  #########################
  # Marianas UMI Clipping #
  #########################

  umi_clipping:
    run: ../cwl_tools/marianas/ProcessLoopUMIFastq.cwl
    in:
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      umi_length: umi_length
      output_project_folder: output_project_folder
    out: [processed_fastq_1, processed_fastq_2, info, output_sample_sheet, umi_frequencies]
    scatter: [fastq1, fastq2, sample_sheet]
    scatterMethod: dotproduct

  ####################
  # Adapted Module 1 #
  ####################

  module_1_innovation:
    run: ./module-1.cwl
    in:
      tmp_dir: tmp_dir
      fastq1: umi_clipping/processed_fastq_1
      fastq2: umi_clipping/processed_fastq_2
      adapter: adapter
      adapter2: adapter2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      add_rg_PL: add_rg_PL
      md__create_index: md__create_index
      md__assume_sorted: md__assume_sorted
      md__compression_level: md__compression_level
      md__validation_stringency: md__validation_stringency
      md__duplicate_scoring_strategy: md__duplicate_scoring_strategy
    out: [bam, bai, md_metrics]
    scatter: [fastq1, fastq2, adapter, adapter2, add_rg_LB, add_rg_ID, add_rg_PU, add_rg_SM]
    scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
  ############################

  group_bams_by_patient:
    run: ../cwl_tools/expression_tools/group_bams.cwl
    in:
      bams: module_1_innovation/bam
      patient_ids: patient_id
    out:
      [grouped_bams, grouped_patient_ids]

  ####################
  # Adapted Module 2 #
  ####################

  module_2:
    run: ./module-2.cwl
    in:
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      bams: group_bams_by_patient/grouped_bams
      patient_id: group_bams_by_patient/grouped_patient_ids
      fci__rf: fci__rf
      fci__cov: fci__cov
      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__intervals: fci__intervals
      abra__mad: abra__mad
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__create_index: fix_mate_information__create_index
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      bqsr__rf: bqsr__rf
      bqsr__nct: bqsr__nct
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      print_reads__nct: print_reads__nct
      print_reads__EOQ: print_reads__EOQ
      print_reads__baq: print_reads__baq

    out: [standard_bams, standard_bais, covint_list, covint_bed]
    scatter: [bams, patient_id]
    scatterMethod: dotproduct

  ################################
  # Return to flat array of bams #
  ################################

  flatten_array_bams:
    run: ../cwl_tools/expression_tools/flatten_array_bam.cwl
    in:
      bams: module_2/standard_bams
    out: [output_bams]
