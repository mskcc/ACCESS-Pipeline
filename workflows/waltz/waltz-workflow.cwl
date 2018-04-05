#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}

inputs:

  input_bam:
    type: File
    secondaryFiles: [^.bai]
  coverage_threshold: int
  gene_list: File
  bed_file: File
  min_mapping_quality: int
  reference_fasta: string
  reference_fasta_fai: string

outputs:
  pileup:
    type: File
    outputSource: pileup_metrics/pileup

  waltz_output_files:
    type:
      type: array
      items: File
    outputSource: grouped_waltz_files/waltz_files

steps:

  count_reads:
    run: ../../cwl_tools/waltz/CountReads.cwl
    in:
      input_bam: input_bam
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
      input_bam: input_bam
      min_mapping_quality: min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      bed_file: bed_file
    out: [
      pileup,
      pileup_without_duplicates,
      intervals,
      intervals_without_duplicates
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
