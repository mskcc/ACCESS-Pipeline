#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:

  tmp_dir: string
  fastq1: File
  fastq2: File
  reference_fasta: string
  reference_fasta_fai: string
  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string
  output_suffix: string

outputs:

  bam:
    type: File
    outputSource: picard.AddOrReplaceReadGroups/bam

  bai:
    type: File
    outputSource: picard.AddOrReplaceReadGroups/bai

steps:

  bwa_mem:
    run: ../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      fastq1: fastq1
      fastq2: fastq2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      ID: add_rg_ID
      LB: add_rg_LB
      SM: add_rg_SM
      PL: add_rg_PL
      PU: add_rg_PU
      CN: add_rg_CN
      output_suffix: output_suffix
    out: [output_sam]

  picard.AddOrReplaceReadGroups:
    run: ../cwl_tools/picard/AddOrReplaceReadGroups.cwl
    in:
      input_bam: bwa_mem/output_sam
      LB: add_rg_LB
      PL: add_rg_PL
      ID: add_rg_ID
      PU: add_rg_PU
      SM: add_rg_SM
      CN: add_rg_CN

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
