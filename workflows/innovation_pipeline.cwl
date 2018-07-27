#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}

inputs:

  tmp_dir: string
  run_tools:
    type:
      type: record
      fields:
        perl_5: string
        java_7: string
        java_8: string
        marianas_path: string
        trimgalore_path: string
        bwa_path: string
        arrg_path: string
        picard_path: string
        gatk_path: string
        abra_path: string
        fx_path: string
        waltz_path: string

  title_file: File
  inputs_yaml: File
  # Todo: This needs to exist in the inputs.yaml,
  # so it needs to exist here, but it isn't used
  version: string

  fastq1: File[]
  fastq2: File[]
  sample_sheet: File[]
  patient_id: string[]
  class_list: string[]

  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file?
  # so we need to use strings here instead of file types
  reference_fasta: string
  reference_fasta_fai: string
  umi_length: int
  output_project_folder: string

  adapter: string[]?
  adapter2: string[]?
  trim__length: int
  trim__paired: boolean
  trim__gzip: boolean
  trim__quality: int
  trim__stringency: int
  trim__suppress_warn: boolean

  add_rg_PL: string
  add_rg_CN: string
  add_rg_LB: int[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]
  md__assume_sorted: boolean
  md__compression_level: int
  md__create_index: boolean
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string
  fci__minbq: int
  fci__minmq: int
  fci__cov: int
  fci__rf: string[]
  fci__intervals: string[]?
  abra__kmers: string
  abra__scratch: string
  abra__mad: int
  fix_mate_information__sort_order: string
  fix_mate_information__validation_stringency: string
  fix_mate_information__compression_level: int
  fix_mate_information__create_index: boolean
  bqsr__nct: int
  bqsr__knownSites_dbSNP: File
  bqsr__knownSites_millis: File
  bqsr__rf: string
  print_reads__nct: int
  print_reads__EOQ: boolean
  print_reads__baq: string
  marianas__mismatches: int
  marianas__wobble: int
  marianas__min_mapping_quality: int
  marianas__min_base_quality: int
  marianas__min_consensus_percent: int

  coverage_threshold: int
  waltz__min_mapping_quality: int
  fci_2__basq_fix: boolean?
  pool_a_bed_file: File
  pool_b_bed_file: File
  A_on_target_positions: File
  B_on_target_positions: File
  noise__good_positions_A: File
  gene_list: File
  FP_config_file: File

outputs:

  clipping_info:
    type: File[]
    outputSource: standard_bam_generation/clipping_info

  bam_dirs:
    type: Directory[]
    outputSource: make_bam_output_directories/directory

  clstats1:
    type: File[]
    outputSource: standard_bam_generation/clstats1

  clstats2:
    type: File[]
    outputSource: standard_bam_generation/clstats2

  md_metrics:
    type: File[]
    outputSource: standard_bam_generation/md_metrics

  fci_covint_list:
    type: File[]
    outputSource: standard_bam_generation/covint_list

  fci_covint_bed:
    type: File[]
    outputSource: standard_bam_generation/covint_bed

  combined_qc:
    type: Directory
    outputSource: qc_workflow/combined_qc

steps:

  #####################
  # Generate Std Bams #
  #####################

  standard_bam_generation:
    run: ./standard_pipeline.cwl
    in:
      run_tools: run_tools
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      umi_length: umi_length
      output_project_folder: output_project_folder
      tmp_dir: tmp_dir

      adapter: adapter
      adapter2: adapter2
      trim__length: trim__length
      trim__paired: trim__paired
      trim__gzip: trim__gzip
      trim__quality: trim__quality
      trim__stringency: trim__stringency
      trim__suppress_warn: trim__suppress_warn

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      md__create_index: md__create_index
      md__assume_sorted: md__assume_sorted
      md__compression_level: md__compression_level
      md__validation_stringency: md__validation_stringency
      md__duplicate_scoring_strategy: md__duplicate_scoring_strategy
      patient_id: patient_id
      reference_fasta: reference_fasta
      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__cov: fci__cov
      fci__rf: fci__rf
      fci__intervals: fci__intervals
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      abra__mad: abra__mad
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__create_index: fix_mate_information__create_index
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      bqsr__nct: bqsr__nct
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      bqsr__rf: bqsr__rf
      print_reads__nct: print_reads__nct
      print_reads__EOQ: print_reads__EOQ
      print_reads__baq: print_reads__baq
    out: [
      standard_bams,
      clipping_dirs,
      clipping_info,
      clstats1,
      clstats2,
      md_metrics,
      covint_list,
      covint_bed]

  ##############################
  # Get pileups for collapsing #
  ##############################

  waltz_standard_pool_a:
    run: ./waltz/waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: standard_bam_generation/standard_bams
      bed_file: pool_a_bed_file
      gene_list: gene_list
      coverage_threshold: coverage_threshold
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  #####################
  # Collapse Std Bams #
  #####################

  umi_collapsing:
    run: ./marianas/marianas_collapsing_workflow.cwl
    in:
      run_tools: run_tools
      input_bam: standard_bam_generation/standard_bams
      pileup: waltz_standard_pool_a/pileup
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      mismatches: marianas__mismatches
      wobble: marianas__wobble
      min_mapping_quality: marianas__min_mapping_quality
      min_base_quality: marianas__min_base_quality
      min_consensus_percent: marianas__min_consensus_percent
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
    out: [
      collapsed_bams,
      first_pass_output_file,
      first_pass_alt_allele,
      first_pass_alt_allele_sorted,
      second_pass_alt_alleles,
      collapsed_fastq_1,
      collapsed_fastq_2]
    scatter: [
      input_bam,
      pileup,
      add_rg_LB,
      add_rg_ID,
      add_rg_PU,
      add_rg_SM]
    scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
  # and run Abra a 2nd time  #
  ############################

#  group_bams_by_patient:
#    run: ../cwl_tools/expression_tools/group_bams.cwl
#    in:
#      bams: umi_collapsing/collapsed_bams
#      patient_ids: patient_id
#    out:
#      [grouped_bams, grouped_patient_ids]
#
#  abra_workflow:
#    run: ABRA/abra_workflow.cwl
#    in:
#      run_tools: run_tools
#      reference_fasta: reference_fasta
#      tmp_dir: tmp_dir
#      bams: group_bams_by_patient/grouped_bams
#      patient_id: group_bams_by_patient/grouped_patient_ids
#      fci__minbq: fci__minbq
#      fci__minmq: fci__minmq
#      fci__rf: fci__rf
#      fci__cov: fci__cov
#      fci__intervals: fci__intervals
#      fci__basq_fix: fci_2__basq_fix
#      abra__mad: abra__mad
#      abra__kmers: abra__kmers
#      abra__scratch: abra__scratch
#      fix_mate_information__sort_order: fix_mate_information__sort_order
#      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
#      fix_mate_information__compression_level: fix_mate_information__compression_level
#      fix_mate_information__create_index: fix_mate_information__create_index
#    out: [ir_bams]
#    scatter: [bams, patient_id]
#    scatterMethod: dotproduct
#
#  ################################
#  # Return to flat array of bams #
#  ################################
#
#  flatten_array_bams:
#    run: ../cwl_tools/expression_tools/flatten_array_bam.cwl
#    in:
#      bams: abra_workflow/ir_bams
#    out: [output_bams]

  ################
  # SeparateBams #
  ################

  separate_bams:
    run: ../cwl_tools/marianas/SeparateBams.cwl
    in:
      run_tools: run_tools
      java_8:
        valueFrom: ${return inputs.run_tools.java_8}
      marianas_path:
        valueFrom: ${return inputs.run_tools.marianas_path}
      collapsed_bam: umi_collapsing/collapsed_bams
    out: [simplex_bam, duplex_bam]
    scatter: [collapsed_bam]
    scatterMethod: dotproduct

  ##################################
  # Make sample output directories #
  ##################################

  # Todo: test that these directories are correctly created
  make_bam_output_directories:
    run: ../cwl_tools/expression_tools/make_sample_output_dirs.cwl
    in:
      standard_bam: standard_bam_generation/standard_bams
      unfiltered_bam: umi_collapsing/collapsed_bams
      simplex_bam: separate_bams/simplex_bam
      duplex_bam: separate_bams/duplex_bam
      r1_fastq: umi_collapsing/collapsed_fastq_1
      r2_fastq: umi_collapsing/collapsed_fastq_2
      first_pass_file: umi_collapsing/first_pass_output_file
      first_pass_sorted: umi_collapsing/first_pass_alt_allele_sorted
      first_pass_alt_alleles: umi_collapsing/first_pass_alt_allele
      second_pass: umi_collapsing/second_pass_alt_alleles
    scatter: [
      standard_bam,
      unfiltered_bam,
      simplex_bam,
      duplex_bam,
      r1_fastq,
      r2_fastq,
      first_pass_file,
      first_pass_sorted,
      first_pass_alt_alleles,
      second_pass]
    scatterMethod: dotproduct
    out: [directory]

  ######
  # QC #
  ######

  qc_workflow:
    run: ./QC/qc_workflow.cwl
    in:
      run_tools: run_tools
      sample_directories: make_bam_output_directories/directory
      A_on_target_positions: A_on_target_positions
      B_on_target_positions: B_on_target_positions
      noise__good_positions_A: noise__good_positions_A
      title_file: title_file
      inputs_yaml: inputs_yaml
      pool_a_bed_file: pool_a_bed_file
      pool_b_bed_file: pool_b_bed_file
      gene_list: gene_list
      coverage_threshold: coverage_threshold
      waltz__min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      standard_bams: standard_bam_generation/standard_bams
      marianas_unfiltered_bams: umi_collapsing/collapsed_bams
      marianas_simplex_bams: separate_bams/simplex_bam
      marianas_duplex_bams: separate_bams/duplex_bam
      FP_config_file: FP_config_file
    out: [combined_qc]
