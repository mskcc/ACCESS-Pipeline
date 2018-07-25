#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}

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

  title_file: File
  pool_a_bed_file: File
  pool_b_bed_file: File
  gene_list: File
  coverage_threshold: int
  waltz__min_mapping_quality: int
  reference_fasta: string
  reference_fasta_fai: string

  standard_bams: File[]
  marianas_unfiltered_bams: File[]
  marianas_simplex_duplex_bams: File[]
  marianas_duplex_bams: File[]

outputs:

  waltz_standard_pool_a_files:
    type: Directory
    outputSource: standard_pool_a_consolidate_bam_metrics/directory

  waltz_unfiltered_pool_a_files:
    type: Directory
    outputSource: unfiltered_pool_a_consolidate_bam_metrics/directory

  waltz_simplex_duplex_pool_a_files:
    type: Directory
    outputSource: simplex_duplex_pool_a_consolidate_bam_metrics/directory

  waltz_duplex_pool_a_files:
    type: Directory
    outputSource: duplex_pool_a_consolidate_bam_metrics/directory

  waltz_standard_pool_b_files:
    type: Directory
    outputSource: standard_pool_b_consolidate_bam_metrics/directory

  waltz_unfiltered_pool_b_files:
    type: Directory
    outputSource: unfiltered_pool_b_consolidate_bam_metrics/directory

  waltz_simplex_duplex_pool_b_files:
    type: Directory
    outputSource: simplex_duplex_pool_b_consolidate_bam_metrics/directory

  waltz_duplex_pool_b_files:
    type: Directory
    outputSource: duplex_pool_b_consolidate_bam_metrics/directory

steps:

  waltz_standard_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: standard_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_a_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  waltz_unfiltered_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: marianas_unfiltered_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_a_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_simplex_duplex_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: marianas_simplex_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_a_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_duplex_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: marianas_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_a_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_standard_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: standard_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_b_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  waltz_unfiltered_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: marianas_unfiltered_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_b_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_simplex_duplex_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: marianas_simplex_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_b_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_duplex_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      input_bam: marianas_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: pool_b_bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  ############################
  # Group waltz output files #
  ############################

  standard_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_standard_a')
      files: waltz_standard_pool_a/waltz_output_files
    out:
      [directory]

  unfiltered_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_unfiltered_a')
      files: waltz_unfiltered_pool_a/waltz_output_files
    out:
      [directory]

  simplex_duplex_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_simplex_duplex_a')
      files: waltz_simplex_duplex_pool_a/waltz_output_files
    out:
      [directory]

  duplex_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_duplex_a')
      files: waltz_duplex_pool_a/waltz_output_files
    out:
      [directory]

  standard_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_standard_b')
      files: waltz_standard_pool_b/waltz_output_files
    out:
      [directory]

  unfiltered_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_unfiltered_b')
      files: waltz_unfiltered_pool_b/waltz_output_files
    out:
      [directory]

  simplex_duplex_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_simplex_duplex_b')
      files: waltz_simplex_duplex_pool_b/waltz_output_files
    out:
      [directory]

  duplex_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_duplex_b')
      files: waltz_duplex_pool_b/waltz_output_files
    out:
      [directory]
