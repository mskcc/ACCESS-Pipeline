#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  input_bam: File

  tmp_dir: string
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
    outputSource: post_collapsing_realignment/bam

steps:

  sort_bam_queryname:
    run: ../../cwl_tools/samtools/sort-by-queryname.cwl
    in:
      input_bam: input_bam
    out:
      [bam_sorted_queryname]

  samtools_fastq:
    run: ../../cwl_tools/samtools/fastq.cwl
    in:
      input_bam: sort_bam_queryname/bam_sorted_queryname
    out:
      [output_read_1, output_read_2]

  gzip_1:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_1
    out:
      [output]

  gzip_2:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_2
    out:
      [output]

  post_collapsing_realignment:
    run: ../../workflows/module-1_abbrev.cwl
    in:
      tmp_dir: tmp_dir
      fastq1: gzip_1/output
      fastq2: gzip_2/output
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix: output_suffix
    out:
      [bam]
