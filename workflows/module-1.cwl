#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
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
        fastqc_path: string?
        cutadapt_path: string?
        bwa_path: string
        arrg_path: string
        picard_path: string

  sample: 'fastq_pair.yml#FastqPair'

  tmp_dir: string
  reference_fasta: string
  reference_fasta_fai: string
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

      fastqc_path:
        valueFrom: $(inputs.run_tools.fastqc_path)
      cutadapt_path:
        valueFrom: $(inputs.run_tools.cutadapt_path)

      adapter:
        source: sample
        valueFrom: $(self.adapter)
      adapter2:
        source: sample
        valueFrom: $(self.adapter2)
      fastq1:
        source: sample
        valueFrom: $(self.fastq1)
      fastq2:
        source: sample
        valueFrom: $(self.fastq2)

    out: [clfastq1, clfastq2, clstats1, clstats2]

  bwa_mem:
    run: ../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      run_tools: run_tools
      bwa:
        valueFrom: $(inputs.run_tools.bwa_path)

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      fastq1: trimgalore/clfastq1
      fastq2: trimgalore/clfastq2

      ID:
        source: sample
        valueFrom: $(self.ID)
      LB:
        source: sample
        valueFrom: $(self.LB)
      SM:
        source: sample
        valueFrom: $(self.SM)
      PL:
        source: sample
        valueFrom: $(self.PL)
      PU:
        source: sample
        valueFrom: $(self.PU)
      CN:
        source: sample
        valueFrom: $(self.CN)

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
      ID:
        source: sample
        valueFrom: $(self.ID)
      LB:
        source: sample
        valueFrom: $(self.LB)
      SM:
        source: sample
        valueFrom: $(self.SM)
      PL:
        source: sample
        valueFrom: $(self.PL)
      PU:
        source: sample
        valueFrom: $(self.PU)
      CN:
        source: sample
        valueFrom: $(self.CN)
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
    out: [bam, bai, mdmetrics]

  collect_output:
    run: ../cwl_tools/expression_tools/collect_bam_output.cwl
    in:
      bam: picard.MarkDuplicates/bam
      sample: sample
    out:
      [bam_out]
