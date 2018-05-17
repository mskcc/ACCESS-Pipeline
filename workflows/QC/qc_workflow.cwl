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

  standard_bams:
    type:
      type: array
      items: File
  marianas_unfiltered_bams:
    type:
      type: array
      items: File
  marianas_simplex_duplex_bams:
    type:
      type: array
      items: File
  marianas_duplex_bams:
    type:
      type: array
      items: File

outputs:

  qc_pdf:
    type: File[]
    outputSource: duplex_innovation_qc/qc_pdf

steps:

  ##############
  # Waltz Runs #
  ##############

  # Todo: this currently gets run 2x
  waltz_standard_pool_a:
    run: ../waltz/waltz-workflow.cwl
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
    run: ../waltz/waltz-workflow.cwl
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
    run: ../waltz/waltz-workflow.cwl
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
    run: ../waltz/waltz-workflow.cwl
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

  # Todo: this currently gets run 2x
  waltz_standard_pool_b:
    run: ../waltz/waltz-workflow.cwl
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
    run: ../waltz/waltz-workflow.cwl
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
    run: ../waltz/waltz-workflow.cwl
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
    run: ../waltz/waltz-workflow.cwl
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
      files: waltz_standard_pool_a/waltz_output_files
    out:
      [directory]

  unfiltered_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      files: waltz_unfiltered_pool_a/waltz_output_files
    out:
      [directory]

  simplex_duplex_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      files: waltz_simplex_duplex_pool_a/waltz_output_files
    out:
      [directory]

  duplex_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      files: waltz_duplex_pool_a/waltz_output_files
    out:
      [directory]

  standard_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      files: waltz_standard_pool_b/waltz_output_files
    out:
      [directory]

  unfiltered_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      files: waltz_unfiltered_pool_b/waltz_output_files
    out:
      [directory]

  simplex_duplex_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      files: waltz_simplex_duplex_pool_b/waltz_output_files
    out:
      [directory]

  duplex_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      files: waltz_duplex_pool_b/waltz_output_files
    out:
      [directory]

  ########################################
  # Aggregate Bam Metrics across samples #
  # for each collapsing method           #
  ########################################

  standard_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: standard_pool_a_consolidate_bam_metrics/directory
    out:
      [output_dir]

  unfiltered_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: unfiltered_pool_a_consolidate_bam_metrics/directory
    out:
      [output_dir]

  simplex_duplex_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: simplex_duplex_pool_a_consolidate_bam_metrics/directory
    out:
      [output_dir]

  duplex_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: duplex_pool_a_consolidate_bam_metrics/directory
    out:
      [output_dir]

  standard_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: standard_pool_b_consolidate_bam_metrics/directory
    out:
      [output_dir]

  unfiltered_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: unfiltered_pool_b_consolidate_bam_metrics/directory
    out:
      [output_dir]

  simplex_duplex_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: simplex_duplex_pool_b_consolidate_bam_metrics/directory
    out:
      [output_dir]

  duplex_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: duplex_pool_b_consolidate_bam_metrics/directory
    out:
      [output_dir]

  #################
  # Innovation-QC #
  #################

  duplex_innovation_qc:
    run: ../../cwl_tools/python/innovation-qc.cwl
    in:
      title_file: title_file
      standard_waltz_metrics_pool_a: standard_aggregate_bam_metrics_pool_a/output_dir
      unfiltered_waltz_metrics_pool_a: unfiltered_aggregate_bam_metrics_pool_a/output_dir
      simplex_duplex_waltz_metrics_pool_a: simplex_duplex_aggregate_bam_metrics_pool_a/output_dir
      duplex_waltz_metrics_pool_a: duplex_aggregate_bam_metrics_pool_a/output_dir

      standard_waltz_metrics_pool_b: standard_aggregate_bam_metrics_pool_b/output_dir
      unfiltered_waltz_metrics_pool_b: unfiltered_aggregate_bam_metrics_pool_b/output_dir
      simplex_duplex_waltz_metrics_pool_b: simplex_duplex_aggregate_bam_metrics_pool_b/output_dir
      duplex_waltz_metrics_pool_b: duplex_aggregate_bam_metrics_pool_b/output_dir
    out:
      [qc_pdf]
