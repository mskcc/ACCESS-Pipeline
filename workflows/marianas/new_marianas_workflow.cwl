#!/usr/bin/env cwl-runner

cwlVersion: v1.0

# Todo: consider making Duplex and Simplex a single workflow
class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

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

  input_bam: File
  reference_fasta: string
  reference_fasta_fai: string
  pileup: File
  mismatches: int
  wobble: int
  min_mapping_quality: int
  min_base_quality: int
  min_consensus_percent: int

  patient_id: string[]

  tmp_dir: string
  reference_fasta: string
  reference_fasta_fai: string
  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string

outputs:

  collapsed_bams:
    type: File
    outputSource: post_collapsing_realignment/bam

steps:

  do_it:
    run: ../../cwl_tools/marianas/process-umi-bam.cwl
    in:
      bam: input_bam
      pileup: pileup
    out:
      []

  post_collapsing_realignment:
    run: ./collapsed_fastq_to_bam.cwl
    in:
      run_tools: run_tools
      patient_id: patient_id
      tmp_dir: tmp_dir
      fastq1: rename_fastq_1/renamed_file
      fastq2: rename_fastq_2/renamed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix:
        valueFrom: ${return '_MC_'}
    out: [bam, bai]
