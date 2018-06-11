#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
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

  bams:
    type:
      type: array
      items: File
    secondaryFiles:
      - ^.bai

  tmp_dir: string
  reference_fasta: string
  patient_id: string

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
  bqsr__rf: string
  bqsr__knownSites_dbSNP:
    type: File
    secondaryFiles:
      - .idx
  bqsr__knownSites_millis:
    type: File
    secondaryFiles:
      - .idx
  print_reads__nct: int
  print_reads__EOQ: boolean
  print_reads__baq: string

outputs:

  standard_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
    outputSource: BQSR_workflow/bqsr_bams

  standard_bais:
    type: File[]
    outputSource: BQSR_workflow/bqsr_bais

  covint_list:
    type: File
    outputSource: ABRA_workflow/covint_list

  covint_bed:
    type: File
    outputSource: ABRA_workflow/covint_bed

steps:

  ABRA_workflow:
    run: ABRA/abra_workflow.cwl
    in:
      run_tools: run_tools
      bams: bams
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      patient_id: patient_id
      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__cov: fci__cov
      fci__rf: fci__rf
      fci__intervals: fci__intervals
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      abra__mad: abra__mad
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__create_index: fix_mate_information__create_index
    out: [ir_bams, covint_list, covint_bed]

  BQSR_workflow:
    run: BQSR/bqsr_workflow.cwl
    in:
      run_tools: run_tools
      bams: ABRA_workflow/ir_bams
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      bqsr__nct: bqsr__nct
      bqsr__rf: bqsr__rf
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      print_reads__nct: print_reads__nct
      print_reads__EOQ: print_reads__EOQ
      print_reads__baq: print_reads__baq
    out: [bqsr_bams, bqsr_bais]
