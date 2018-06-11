#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

doc: |
  This workflow is intended to be used to test the QC module,
  without having to run the long waltz step

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 3000
    coresMin: 2

inputs:
  title_file: File
  FP_config_file: File
  sample_directories: Directory[]
  A_on_target_positions: File
  B_on_target_positions: File
  noise__good_positions_A: File

  waltz_standard_pool_a: Directory
  waltz_unfiltered_pool_a: Directory
  waltz_simplex_duplex_pool_a: Directory
  waltz_duplex_pool_a: Directory
  waltz_standard_pool_b: Directory
  waltz_unfiltered_pool_b: Directory
  waltz_simplex_duplex_pool_b: Directory
  waltz_duplex_pool_b: Directory

outputs:

  qc_pdf:
    type: File[]
    outputSource: innovation_qc/qc_pdf

  combined_qc:
    type: File
    outputSource: combine_qc/combined_qc

steps:

  ########################################
  # Aggregate Bam Metrics across samples #
  # for each collapsing method           #
  ########################################

  standard_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_standard_pool_a
    out:
      [output_dir]

  unfiltered_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_unfiltered_pool_a
    out:
      [output_dir]

  simplex_duplex_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_simplex_duplex_pool_a
    out:
      [output_dir]

  duplex_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_duplex_pool_a
    out:
      [output_dir]

  standard_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_standard_pool_b
    out:
      [output_dir]

  unfiltered_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_unfiltered_pool_b
    out:
      [output_dir]

  simplex_duplex_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_simplex_duplex_pool_b
    out:
      [output_dir]

  duplex_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      title_file: title_file
      waltz_input_files: waltz_duplex_pool_b
    out:
      [output_dir]

  ##################
  # Fingerprinting #
  ##################

  fingerprinting:
    run: ../../cwl_tools/python/fingerprinting.cwl
    in:
      output_directory:
        valueFrom: ${return '.'}
      waltz_directory_A: waltz_unfiltered_pool_a
      waltz_directory_B: waltz_unfiltered_pool_b
      FP_config_file: FP_config_file
      title_file: title_file
    out: [
      all_fp_results,
      FPFigures]

  #########
  # Noise #
  #########

  noise_tables:
    run: ../../cwl_tools/noise/calculate_noise.cwl
    in:
      waltz_directory: waltz_duplex_pool_a
      good_positions_A: noise__good_positions_A
    out: [noise, noise_by_substitution]

  noise_plots:
    run: ../../cwl_tools/noise/plot_noise.cwl
    in:
      noise: noise_tables/noise
      noise_by_substitution: noise_tables/noise_by_substitution
    out: [noise_alt_percent, noise_contributing_sites]

  ##########
  # UMI QC #
  ##########

  umi_qc_tables:
    run: ../../cwl_tools/umi_qc/make_umi_qc_tables.cwl
    in:
      A_on_target_positions: A_on_target_positions
      B_on_target_positions: B_on_target_positions
      folders: sample_directories
    out: [
      family_sizes,
      family_types_A,
      family_types_B]

  umi_qc_plots:
    run: ../../cwl_tools/umi_qc/plot_umi_qc.cwl
    in:
      family_sizes: umi_qc_tables/family_sizes
    out: [plots]

  #######################################
  # Combine FP, UMI, & Noise qc results #
  #######################################

  combine_qc:
    run: ../../cwl_tools/python/combine_qc_pdfs.cwl
    in:
      umi_qc: umi_qc_plots/plots
      noise_alt_percent: noise_plots/noise_alt_percent
      noise_contributing_sites: noise_plots/noise_contributing_sites
      fingerprinting_qc: fingerprinting/FPFigures
    out:
      [combined_qc]

  ###############
  # Standard-QC #
  ###############

  innovation_qc:
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
    out: [qc_pdf]
