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
    outputSource: duplex_innovation_qc/qc_pdf

  all_fp_results:
    type: Directory
    outputSource: fingerprinting/all_fp_results

  FPFigures:
    type: File
    outputSource: fingerprinting/FPFigures

  noise_table:
    type: File
    outputSource: noise/noise

  noise_by_substitution:
    type: File
    outputSource: noise/noise_by_substitution

  noise_alt_percent:
    type: File
    outputSource: plot_noise/noise_alt_percent

  noise_contributing_sites:
    type: File
    outputSource: plot_noise/noise_contributing_sites

  umi_qc:
    type: File[]
    outputSource: umi_qc_plots/plots

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

#  concat_pileups:
#    in:
#      pileup_A: standard_aggregate_bam_metrics_pool_a/pileup
#      pileup_B: standard_aggregate_bam_metrics_pool_b/pileup
#    out: [pileups_concat]
#    scatter: [pileup_A, pileup_B]

  fingerprinting:
    run: ../../cwl_tools/python/fingerprinting.cwl
    in:
      output_directory:
        valueFrom: ${return '.'}
      waltz_directory: waltz_standard_pool_a
      FP_config_file: FP_config_file
    out: [
      all_fp_results,
      FPFigures]

  #########
  # Noise #
  #########

  noise:
    run: ../../cwl_tools/noise/calculate_noise.cwl
    in:
      waltz_directory: waltz_duplex_pool_a
    out: [noise, noise_by_substitution]

  plot_noise:
    run: ../../cwl_tools/noise/plot_noise.cwl
    in:
      output_dir:
        valueFrom: ${return '.'}
      noise: noise/noise
      noise_by_substitution: noise/noise_by_substitution
    out: [noise_alt_percent, noise_contributing_sites]

  ##########
  # UMI QC #
  ##########

  umi_qc_tables:
    run: ../../cwl_tools/umi_qc/make_umi_qc_tables.cwl
    in:
      folders: sample_directories
      A_on_target_positions: A_on_target_positions
      B_on_target_positions: B_on_target_positions
    out: [
      cluster_sizes,
      cluster_sizes_post_filtering,
      clusters_per_position,
      clusters_per_position_post_filtering,
      family_types_A,
      family_types_B]

  umi_qc_plots:
    run: ../../cwl_tools/umi_qc/umi_qc.cwl
    in:
      cluster_sizes: umi_qc_tables/cluster_sizes
      cluster_sizes_post_filtering: umi_qc_tables/cluster_sizes_post_filtering
      clusters_per_position: umi_qc_tables/clusters_per_position
      clusters_per_position_post_filtering: umi_qc_tables/clusters_per_position_post_filtering
      family_types_A: umi_qc_tables/family_types_A
      family_types_B: umi_qc_tables/family_types_B
    out: [plots]

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
    out: [qc_pdf]
