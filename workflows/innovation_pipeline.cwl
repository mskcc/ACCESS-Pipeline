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
        fastqc_path: string?
        cutadapt_path: string?
        waltz_path: string

  title_file: File
  fastq1: File[]
  fastq2: File[]
  sample_sheet: File[]
  patient_id: string[]
  # List of ['Tumor', 'Normal', ...] sample class values
  class_list: string[]

  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file?
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

  md__assume_sorted: boolean
  md__compression_level: int
  md__create_index: boolean
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string

  # Module 2
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

  # Fulcrum
  tmp_dir: string
  fulcrum__sort_order: string
  fulcrum__grouping_strategy: string
  fulcrum__min_mapping_quality: int
  fulcrum__tag_family_size_counts_output: string
  fulcrum__call_duplex_min_reads: string
  fulcrum__filter_min_base_quality: int
  fulcrum__filter_min_reads__simplex_duplex: string
  fulcrum__filter_min_reads__duplex: string

  # Marianas
  marianas__mismatches: int
  marianas__wobble: int
  marianas__min_mapping_quality: int
  marianas__min_base_quality: int
  marianas__min_consensus_percent: int

  # Waltz
  bed_file: File
  gene_list: File
  coverage_threshold: int
  waltz__min_mapping_quality: int

outputs:

  standard_bams:
    type:
      type: array
      items: File
    outputSource: standard_bam_generation/standard_bams

  unfiltered_bams:
    type:
      type: array
      items: File
    outputSource: flatten_array_bams/output_bams

  simplex_duplex_bams:
    type:
      type: array
      items: File
    outputSource: separate_bams/simplex_duplex_bam

  duplex_bams:
    type:
      type: array
      items: File
    outputSource: separate_bams/duplex_bam

steps:

  standard_bam_generation:
    run: ./standard_pipeline.cwl
    in:
      run_tools: run_tools
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      # Process Loop Umi Fastq
      umi_length: umi_length
      output_project_folder: output_project_folder
      # Module 1
      tmp_dir: tmp_dir
      adapter: adapter
      adapter2: adapter2
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

      # Group bams by patient
      patient_id: patient_id
      # Module 2
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
    out: [standard_bams]

  waltz_standard:
    run: ./waltz/waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: standard_bam_generation/standard_bams
      bed_file: bed_file
      gene_list: gene_list
      coverage_threshold: coverage_threshold
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  group_pileups:
    run: ../cwl_tools/expression_tools/group_pileups.cwl
    in:
      pileups: waltz_standard/pileup
      bams: standard_bam_generation/standard_bams
      patient_ids: patient_id
      class_list: class_list
    out: [ordered_bams, ordered_patient_ids, ordered_pileups]

  umi_collapsing:
    run: ./marianas/marianas_collapsing_workflow.cwl
    in:
      run_tools: run_tools
      input_bam: group_pileups/ordered_bams
      pileup: group_pileups/ordered_pileups
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      mismatches: marianas__mismatches
      wobble: marianas__wobble
      min_mapping_quality: marianas__min_mapping_quality
      min_base_quality: marianas__min_base_quality
      min_consensus_percent: marianas__min_consensus_percent

      # Group bams by patient
      patient_id: patient_id

      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
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

    out: [collapsed_bams]
    scatter: [
      input_bam,
      pileup,
      add_rg_LB,
      add_rg_ID,
      add_rg_PU,
      add_rg_SM,
    ]
    scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
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
      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__rf: fci__rf
      fci__cov: fci__cov
      fci__intervals: fci__intervals
      abra__mad: abra__mad
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__create_index: fix_mate_information__create_index
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
    out: [simplex_duplex_bam, duplex_bam]
    scatter: [collapsed_bam]
    scatterMethod: dotproduct
