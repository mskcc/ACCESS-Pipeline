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
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/schema_defs/Sample.cwl

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

  samples: ../resources/schema_defs/Sample.cwl#Sample[]

  tmp_dir: string
  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file,
  # so we need to use strings here instead of file types
  reference_fasta: string
  reference_fasta_fai: string

  # Marianas Clipping
  umi_length: int
  output_project_folder: string
  # Module 1
  md__create_index: boolean
  md__assume_sorted: boolean
  md__compression_level: int
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

  output_samples:
    type: ../resources/schema_defs/Sample.cwl#Sample[]
    outputSource: flatten_samples_array/output_samples

steps:

  #########################
  # Marianas UMI Clipping #
  #########################

  umi_clipping:
    run: ../cwl_tools/marianas/ProcessLoopUMIFastq.cwl
    in:
      run_tools: run_tools
      java_8:
        valueFrom: ${return inputs.run_tools.java_8}
      marianas_path:
        valueFrom: ${return inputs.run_tools.marianas_path}

      sample: samples
      fastq1:
        valueFrom: $(inputs.sample.fastq1)
      fastq2:
        valueFrom: $(inputs.sample.fastq2)
      sample_sheet:
        valueFrom: $(inputs.sample.sample_sheet)

      umi_length: umi_length
      output_project_folder: output_project_folder

    out: [output_sample]
    scatter: [sample]
    scatterMethod: dotproduct

  ####################
  # Adapted Module 1 #
  ####################

  module_1:
    run: ./module-1.cwl
    in:
      run_tools: run_tools
      tmp_dir: tmp_dir
      sample: umi_clipping/output_sample
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      md__create_index: md__create_index
      md__assume_sorted: md__assume_sorted
      md__compression_level: md__compression_level
      md__validation_stringency: md__validation_stringency
      md__duplicate_scoring_strategy: md__duplicate_scoring_strategy
    out: [output_sample]
    scatter: [sample]
    scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
  ############################

  group_samples_by_patient:
    run: ../cwl_tools/expression_tools/group_samples_by_patient.cwl
    in:
      samples: module_1/output_sample
    out:
      [grouped_samples]

  ####################
  # Adapted Module 2 #
  ####################

  module_2:
    run: ./module-2.cwl
    in:
      run_tools: run_tools
      tmp_dir: tmp_dir

      samples: group_samples_by_patient/grouped_samples

      reference_fasta: reference_fasta
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
    out: [output_samples]
    scatter: [samples]
    scatterMethod: dotproduct

  ################################
  # Return to flat array of bams #
  ################################

  flatten_samples_array:
    run: ../cwl_tools/expression_tools/flatten_samples_array.cwl
    in:
      samples: module_2/output_samples
    out: [output_samples]
