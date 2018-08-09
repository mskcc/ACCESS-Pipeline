#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SubworkflowFeatureRequirement: {}
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

  tmp_dir: string
  fastq1: File
  fastq2: File

  reference_fasta: string
  reference_fasta_fai: string

  trim__length: int
  trim__paired: boolean
  trim__gzip: boolean
  trim__quality: int
  trim__stringency: int
  trim__suppress_warn: boolean

  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string
  md__assume_sorted: boolean
  md__compression_level: int
  md__create_index: boolean
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string

outputs:

  clstats1:
    type: File
    outputSource: trimgalore/clstats1

  clstats2:
    type: File
    outputSource: trimgalore/clstats2

  bam:
    type: File
    outputSource: picard.MarkDuplicates/bam

  # Todo: unnecessary output
  bai:
    type: File
    outputSource: picard.MarkDuplicates/bai

  md_metrics:
    type: File
    outputSource: picard.MarkDuplicates/mdmetrics

steps:

  trimgalore:
    run: ../cwl_tools/trimgalore/trimgalore.cwl
    in:
      run_tools: run_tools
      perl:
        valueFrom: $(inputs.run_tools.perl_5)
      trimgalore:
        valueFrom: $(inputs.run_tools.trimgalore_path)

      fastq1: fastq1
      fastq2: fastq2
      length: trim__length
      paired: trim__paired
      gzip: trim__gzip
      quality: trim__quality
      stringency: trim__stringency
      suppress_warn: trim__suppress_warn
    out: [clfastq1, clfastq2, clstats1, clstats2]

  bwa_mem:
    run: ../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      run_tools: run_tools
      bwa:
        valueFrom: $(inputs.run_tools.bwa_path)
      fastq1: trimgalore/clfastq1
      fastq2: trimgalore/clfastq2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      ID: add_rg_ID
      LB: add_rg_LB
      SM: add_rg_SM
      PL: add_rg_PL
      PU: add_rg_PU
      CN: add_rg_CN
    out: [output_sam]

  picard.AddOrReplaceReadGroups:
    run: ../cwl_tools/picard/AddOrReplaceReadGroups.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_7)
      arrg:
        valueFrom: $(inputs.run_tools.arrg_path)
      input_bam: bwa_mem/output_sam
      LB: add_rg_LB
      PL: add_rg_PL
      ID: add_rg_ID
      PU: add_rg_PU
      SM: add_rg_SM
      CN: add_rg_CN
      # Todo: Move to inputs.yaml
      sort_order:
        default: 'coordinate'
      validation_stringency:
        default: 'LENIENT'
      compression_level:
        default: 0
      create_index:
        default: true
      tmp_dir: tmp_dir
    out: [bam, bai]

  picard.MarkDuplicates:
    run: ../cwl_tools/picard/MarkDuplicates.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_8)
      picard:
        valueFrom: $(inputs.run_tools.picard_path)
      input_bam: picard.AddOrReplaceReadGroups/bam
      tmp_dir: tmp_dir
      assume_sorted: md__assume_sorted
      compression_level: md__compression_level
      create_index: md__create_index
      validation_stringency: md__validation_stringency
      duplicate_scoring_strategy: md__duplicate_scoring_strategy
    # Todo: unnecessary output
    out: [bam, bai, mdmetrics]
