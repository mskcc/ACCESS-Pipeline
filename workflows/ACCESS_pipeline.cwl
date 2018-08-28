#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_tools/schemas.yaml
      - $import: ../resources/run_params/schemas/process_loop_umi_fastq.yaml
      - $import: ../resources/run_params/schemas/trimgalore.yaml
      - $import: ../resources/run_params/schemas/add_or_replace_read_groups.yaml
      - $import: ../resources/run_params/schemas/mark_duplicates.yaml
      - $import: ../resources/run_params/schemas/find_covered_intervals.yaml
      - $import: ../resources/run_params/schemas/abra.yaml
      - $import: ../resources/run_params/schemas/fix_mate_information.yaml
      - $import: ../resources/run_params/schemas/base_recalibrator.yaml
      - $import: ../resources/run_params/schemas/print_reads.yaml
      - $import: ../resources/run_params/schemas/marianas_collapsing.yaml
      - $import: ../resources/run_params/schemas/waltz.yaml

inputs:

  tmp_dir: string
  run_tools: ../resources/run_tools/schemas.yaml#run_tools

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
  add_rg_LB: int[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]

  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file?
  # so we need to use strings here instead of file types
  reference_fasta: string
  reference_fasta_fai: string

  process_loop_umi_fastq__params: ../resources/run_params/schemas/process_loop_umi_fastq.yaml#process_loop_umi_fastq__params
  trimgalore__params: ../resources/run_params/schemas/trimgalore.yaml#trimgalore__params
  add_or_replace_read_groups__params: ../resources/run_params/schemas/add_or_replace_read_groups.yaml#add_or_replace_read_groups__params
  mark_duplicates__params: ../resources/run_params/schemas/mark_duplicates.yaml#mark_duplicates__params
  find_covered_intervals__params: ../resources/run_params/schemas/find_covered_intervals.yaml#find_covered_intervals__params
  abra__params: ../resources/run_params/schemas/abra.yaml#abra__params
  fix_mate_information__params: ../resources/run_params/schemas/fix_mate_information.yaml#fix_mate_information__params
  base_recalibrator__params: ../resources/run_params/schemas/base_recalibrator.yaml#base_recalibrator__params
  print_reads__params: ../resources/run_params/schemas/print_reads.yaml#print_reads__params
  marianas_collapsing__params: ../resources/run_params/schemas/marianas_collapsing.yaml#marianas_collapsing__params
  waltz__params: ../resources/run_params/schemas/waltz.yaml#waltz__params

  bqsr__knownSites_dbSNP: File
  bqsr__knownSites_millis: File

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
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      patient_id: patient_id

      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM

      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis

      process_loop_umi_fastq__params: process_loop_umi_fastq__params
      trimgalore__params: trimgalore__params
      add_or_replace_read_groups__params: add_or_replace_read_groups__params
      mark_duplicates__params: mark_duplicates__params
      find_covered_intervals__params: find_covered_intervals__params
      abra__params: abra__params
      fix_mate_information__params: fix_mate_information__params
      base_recalibrator__params: base_recalibrator__params
      print_reads__params: print_reads__params

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
      waltz__params: waltz__params
      input_bam: standard_bam_generation/standard_bams
      bed_file: pool_a_bed_file
      gene_list: gene_list
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
      tmp_dir: tmp_dir

      marianas_collapsing__params: marianas_collapsing__params
      add_or_replace_read_groups__params: add_or_replace_read_groups__params

      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM

      add_rg_PL:
        valueFrom: $(inputs.add_or_replace_read_groups__params.add_rg_PL)
      add_rg_CN:
        valueFrom: $(inputs.add_or_replace_read_groups__params.add_rg_CN)

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

  group_bams_by_patient:
    run: ../cwl_tools/expression_tools/group_bams.cwl
    in:
      bams: umi_collapsing/collapsed_bams
      patient_ids: patient_id
    out:
      [grouped_bams, grouped_patient_ids]

  abra_workflow:
    run: ABRA/abra_workflow.cwl
    in:
      run_tools: run_tools
      reference_fasta: reference_fasta
      tmp_dir: tmp_dir
      bams: group_bams_by_patient/grouped_bams
      patient_id: group_bams_by_patient/grouped_patient_ids

      find_covered_intervals__params: find_covered_intervals__params
      abra__params: abra__params
      fix_mate_information__params: fix_mate_information__params
    out: [ir_bams]
    scatter: [bams, patient_id]
    scatterMethod: dotproduct

  ################################
  # Return to flat array of bams #
  ################################

  flatten_array_bams:
    run: ../cwl_tools/expression_tools/flatten_array_bam.cwl
    in:
      bams: abra_workflow/ir_bams
    out: [output_bams]

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
      collapsed_bam: flatten_array_bams/output_bams
    out: [simplex_bam, duplex_bam]
    scatter: [collapsed_bam]
    scatterMethod: dotproduct

  ##################################
  # Make sample output directories #
  ##################################

  make_bam_output_directories:
    run: ../cwl_tools/expression_tools/make_sample_output_dirs.cwl
    in:
      standard_bam: standard_bam_generation/standard_bams
      # Collapsed, and after 2nd Indel Realignment:
      unfiltered_bam: flatten_array_bams/output_bams
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
      waltz__params: waltz__params

      sample_directories: make_bam_output_directories/directory
      A_on_target_positions: A_on_target_positions
      B_on_target_positions: B_on_target_positions
      noise__good_positions_A: noise__good_positions_A
      title_file: title_file
      inputs_yaml: inputs_yaml
      pool_a_bed_file: pool_a_bed_file
      pool_b_bed_file: pool_b_bed_file
      gene_list: gene_list

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      standard_bams: standard_bam_generation/standard_bams
      marianas_unfiltered_bams: umi_collapsing/collapsed_bams
      marianas_simplex_bams: separate_bams/simplex_bam
      marianas_duplex_bams: separate_bams/duplex_bam
      FP_config_file: FP_config_file
    out: [combined_qc]
