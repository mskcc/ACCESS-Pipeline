#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
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
        waltz_path: string

  sample: ../../resources/schema_defs/Sample.cwl#Sample

#  input_bam:
#    type: File
#    secondaryFiles: [^.bai]

  coverage_threshold: int
  gene_list: File
  bed_file: File
  min_mapping_quality: int
  reference_fasta: string
  reference_fasta_fai: string

outputs:
  output_sample:
    type: ../../resources/schema_defs/Sample.cwl#Sample
    outputSource: pileup_metrics/output_sample

  waltz_output_files:
    type:
      type: array
      items: File
    outputSource: grouped_waltz_files/waltz_files

steps:

  count_reads:
    run: ../../cwl_tools/waltz/CountReads.cwl
    in:
      run_tools: run_tools
      java_8:
        valueFrom: ${return inputs.run_tools.java_8}
      waltz_path:
        valueFrom: ${return inputs.run_tools.waltz_path}

      input_bam:
        source: sample
        valueFrom: $(self.standard_bam)

      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
    out: [
      covered_regions,
      fragment_sizes,
      read_counts
    ]

  pileup_metrics:
    run: ../../cwl_tools/waltz/PileupMetrics.cwl
    in:
      run_tools: run_tools
      java_8:
        valueFrom: ${return inputs.run_tools.java_8}
      waltz_path:
        valueFrom: ${return inputs.run_tools.waltz_path}

      sample: sample
      input_bam:
        source: sample
        valueFrom: $(self.standard_bam)

      min_mapping_quality: min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      bed_file: bed_file
    out: [
      pileup,
      pileup_without_duplicates,
      intervals,
      intervals_without_duplicates,
      output_sample
    ]

  grouped_waltz_files:
    run: ../../cwl_tools/expression_tools/group_waltz_files.cwl
    in:
      covered_regions: count_reads/covered_regions
      fragment_sizes: count_reads/fragment_sizes
      read_counts: count_reads/read_counts
      pileup: pileup_metrics/pileup
      pileup_without_duplicates: pileup_metrics/pileup_without_duplicates
      intervals: pileup_metrics/intervals
      intervals_without_duplicates: pileup_metrics/intervals_without_duplicates
    out: [waltz_files]
