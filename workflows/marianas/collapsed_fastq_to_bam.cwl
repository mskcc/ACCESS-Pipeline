#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl

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

  reference_fasta: string
  reference_fasta_fai: string
  sample: ../../resources/schema_defs/Sample.cwl#Sample
  fastq1: File
  fastq2: File

  tmp_dir: string
  output_suffix: string

outputs:

  output_sample:
    type: ../../resources/schema_defs/Sample.cwl#Sample
    outputSource: add_or_replace_read_groups/output_sample

steps:

  bwa_mem:
    run: ../../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      run_tools: run_tools
      bwa:
        valueFrom: ${return inputs.run_tools.bwa_path}

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      sample: sample
      fastq1: fastq1
      fastq2: fastq2
      ID:
        valueFrom: $(inputs.sample.ID)
      LB:
        valueFrom: $(inputs.sample.LB)
      SM:
        valueFrom: $(inputs.sample.SM)
      PL:
        valueFrom: $(inputs.sample.PL)
      PU:
        valueFrom: $(inputs.sample.PU)
      CN:
        valueFrom: $(inputs.sample.CN)
      output_suffix: output_suffix
    out: [output_sample]

  add_or_replace_read_groups:
    run: ../../cwl_tools/picard/AddOrReplaceReadGroups.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_7)
      arrg:
        valueFrom: $(inputs.run_tools.arrg_path)

      sample: bwa_mem/output_sample
      ID:
        valueFrom: $(inputs.sample.ID)
      LB:
        valueFrom: $(inputs.sample.LB)
      SM:
        valueFrom: $(inputs.sample.SM)
      PL:
        valueFrom: $(inputs.sample.PL)
      PU:
        valueFrom: $(inputs.sample.PU)
      CN:
        valueFrom: $(inputs.sample.CN)

      # Todo: Move to inputs.yaml
      sort_order:
        default: coordinate
      validation_stringency:
        default: LENIENT
      compression_level:
        default: 0
      create_index:
        default: true
      tmp_dir: tmp_dir
    out: [output_sample]
