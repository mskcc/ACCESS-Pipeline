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
        fastqc_path: string?
        cutadapt_path: string?
        bwa_path: string
        arrg_path: string
        picard_path: string

  sample: ../resources/schema_defs/Sample.cwl#Sample

  tmp_dir: string
  reference_fasta: string
  reference_fasta_fai: string
  md__assume_sorted: boolean
  md__compression_level: int
  md__create_index: boolean
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string

outputs:
  output_sample:
    type: ../resources/schema_defs/Sample.cwl#Sample
    outputSource: picard.MarkDuplicates/output_sample

steps:

  trimgalore:
    run: ../cwl_tools/trimgalore/trimgalore.cwl
    in:
      run_tools: run_tools
      perl:
        valueFrom: $(inputs.run_tools.perl_5)
      trimgalore:
        valueFrom: $(inputs.run_tools.trimgalore_path)
      fastqc_path:
        valueFrom: $(inputs.run_tools.fastqc_path)
      cutadapt_path:
        valueFrom: $(inputs.run_tools.cutadapt_path)

      sample: sample
      fastq1:
        valueFrom: $(inputs.sample.fastq1)
      fastq2:
        valueFrom: $(inputs.sample.fastq2)
      adapter:
        valueFrom: $(inputs.sample.adapter)
      adapter2:
        valueFrom: $(inputs.sample.adapter2)
    out: [output_sample]

  bwa_mem:
    run: ../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      run_tools: run_tools
      bwa:
        valueFrom: $(inputs.run_tools.bwa_path)

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      sample: trimgalore/output_sample
      fastq1:
        valueFrom: $(inputs.sample.clfastq1)
      fastq2:
        valueFrom: $(inputs.sample.clfastq2)
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
    out: [output_sample]

  picard.AddOrReplaceReadGroups:
    run: ../cwl_tools/picard/AddOrReplaceReadGroups.cwl
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

  picard.MarkDuplicates:
    run: ../cwl_tools/picard/MarkDuplicates.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_8)
      picard:
        valueFrom: $(inputs.run_tools.picard_path)

      sample: picard.AddOrReplaceReadGroups/output_sample
      input_bam:
        valueFrom: $(inputs.sample.rg_bam)

      tmp_dir: tmp_dir
      assume_sorted: md__assume_sorted
      compression_level: md__compression_level
      create_index: md__create_index
      validation_stringency: md__validation_stringency
      duplicate_scoring_strategy: md__duplicate_scoring_strategy
    out: [output_sample]
