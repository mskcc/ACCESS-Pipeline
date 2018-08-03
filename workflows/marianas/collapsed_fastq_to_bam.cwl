#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SubworkflowFeatureRequirement: {}

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
    outputSource: add_or_replace_read_groups/bam

  bai:
    type: File
    outputSource: add_or_replace_read_groups/bai

steps:

  bwa_mem:
    run: ../../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      run_tools: run_tools
      bwa:
        valueFrom: ${return inputs.run_tools.bwa_path}

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
      # Todo: this is not used
      output_suffix: output_suffix
    out: [output_sam]

  add_or_replace_read_groups:
    run: ../../cwl_tools/picard/AddOrReplaceReadGroups.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: ${return inputs.run_tools.java_7}
      arrg:
        valueFrom: ${return inputs.run_tools.arrg_path}

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
