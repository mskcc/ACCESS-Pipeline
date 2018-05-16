#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
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

  samples:
    type:
      type: array
      items: ../resources/schema_defs/Sample.cwl#Sample

  tmp_dir: string
  reference_fasta: string

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

  output_samples:
    type:
      type: array
      items: ../resources/schema_defs/Sample.cwl#Sample
    outputSource: BQSR_workflow/output_samples

steps:

  ABRA_workflow:
    run: ABRA/abra_workflow.cwl
    in:
      run_tools: run_tools
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta

      samples: samples

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
    out: [output_samples]

  BQSR_workflow:
    run: BQSR/bqsr_workflow.cwl
    in:
      run_tools: run_tools
      samples: ABRA_workflow/output_samples

#      bams:
#        valueFrom: $(inputs.samples.map(function(x){ return x.ir_bam }))

      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      bqsr__nct: bqsr__nct
      bqsr__rf: bqsr__rf
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      print_reads__nct: print_reads__nct
      print_reads__EOQ: print_reads__EOQ
      print_reads__baq: print_reads__baq
    out: [output_samples]
