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

inputs:
  title_file: File
  inputs_yaml: File
  FP_config_file: File
  sample_directories: Directory[]
  A_on_target_positions: File
  B_on_target_positions: File
  noise__good_positions_A: File

  waltz_standard_pool_a: Directory
  waltz_unfiltered_pool_a: Directory
  waltz_simplex_pool_a: Directory
  waltz_duplex_pool_a: Directory
  waltz_standard_pool_b: Directory
  waltz_unfiltered_pool_b: Directory
  waltz_simplex_pool_b: Directory
  waltz_duplex_pool_b: Directory

outputs:

  combined_qc:
    type: Directory
    outputSource: group_qc_files/qc_files

steps:

  ########################################
  # Aggregate Bam Metrics across samples #
  # for each collapsing method           #
  ########################################

  standard_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_standard_pool_a
      output_dir_name:
        valueFrom: $('waltz_standard_pool_a')
    out: [output_dir]

  unfiltered_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_unfiltered_pool_a
      output_dir_name:
        valueFrom: $('waltz_unfiltered_pool_a')
    out: [output_dir]

  simplex_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_simplex_pool_a
      output_dir_name:
        valueFrom: $('waltz_simplex_pool_a')
    out: [output_dir]

  duplex_aggregate_bam_metrics_pool_a:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_duplex_pool_a
      output_dir_name:
        valueFrom: $('waltz_duplex_pool_a')
    out: [output_dir]

  standard_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_standard_pool_b
      output_dir_name:
        valueFrom: $('waltz_standard_pool_b')
    out: [output_dir]

  unfiltered_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_unfiltered_pool_b
      output_dir_name:
        valueFrom: $('waltz_unfiltered_pool_b')
    out: [output_dir]

  simplex_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_simplex_pool_b
      output_dir_name:
        valueFrom: $('waltz_simplex_pool_b')
    out: [output_dir]

  duplex_aggregate_bam_metrics_pool_b:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_duplex_pool_b
      output_dir_name:
        valueFrom: $('waltz_duplex_pool_b')
    out: [output_dir]

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
      waltz_directory_A_duplex: waltz_duplex_pool_a
      waltz_directory_B_duplex: waltz_duplex_pool_b
      FP_config_file: FP_config_file
      title_file: title_file
    out: [
      all_fp_results,
      FPFigures,
      gender_table,
      gender_plot]

  #########
  # Noise #
  #########

  standard_noise_tables_A:
    run: ../../cwl_tools/noise/calculate_noise.cwl
    in:
      output_dir_name:
        valueFrom: $('waltz_standard_pool_a')
      waltz_directory: standard_aggregate_bam_metrics_pool_a/output_dir
      good_positions_A: noise__good_positions_A
    out: [noise, noise_by_substitution, waltz_folder_with_noise]

  unfiltered_noise_tables_A:
    run: ../../cwl_tools/noise/calculate_noise.cwl
    in:
      output_dir_name:
        valueFrom: $('waltz_unfiltered_pool_a')
      waltz_directory: unfiltered_aggregate_bam_metrics_pool_a/output_dir
      good_positions_A: noise__good_positions_A
    out: [noise, noise_by_substitution, waltz_folder_with_noise]

  simplex_noise_tables_A:
    run: ../../cwl_tools/noise/calculate_noise.cwl
    in:
      output_dir_name:
        valueFrom: $('waltz_simplex_pool_a')
      waltz_directory: simplex_aggregate_bam_metrics_pool_a/output_dir
      good_positions_A: noise__good_positions_A
    out: [noise, noise_by_substitution, waltz_folder_with_noise]

  duplex_noise_tables_A:
    run: ../../cwl_tools/noise/calculate_noise.cwl
    in:
      output_dir_name:
        valueFrom: $('waltz_duplex_pool_a')
      waltz_directory: duplex_aggregate_bam_metrics_pool_a/output_dir
      good_positions_A: noise__good_positions_A
    out: [noise, noise_by_substitution, waltz_folder_with_noise]


  standard_noise_plots_A:
    run: ../../cwl_tools/noise/plot_noise.cwl
    in:
      title_file: title_file
      noise: standard_noise_tables_A/noise
      noise_by_substitution: standard_noise_tables_A/noise_by_substitution
    out: [noise_alt_percent, noise_contributing_sites]

  unfiltered_noise_plots_A:
    run: ../../cwl_tools/noise/plot_noise.cwl
    in:
      title_file: title_file
      noise: unfiltered_noise_tables_A/noise
      noise_by_substitution: unfiltered_noise_tables_A/noise_by_substitution
    out: [noise_alt_percent, noise_contributing_sites]

  simplex_noise_plots_A:
    run: ../../cwl_tools/noise/plot_noise.cwl
    in:
      title_file: title_file
      noise: simplex_noise_tables_A/noise
      noise_by_substitution: simplex_noise_tables_A/noise_by_substitution
    out: [noise_alt_percent, noise_contributing_sites]

  duplex_noise_plots_A:
    run: ../../cwl_tools/noise/plot_noise.cwl
    in:
      title_file: title_file
      noise: duplex_noise_tables_A/noise
      noise_by_substitution: duplex_noise_tables_A/noise_by_substitution
    out: [noise_alt_percent, noise_contributing_sites]

  #################
  # UMI QC tables #
  #################

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

  ###############
  # Standard-QC #
  ###############

  innovation_qc:
    run: ../../cwl_tools/python/innovation_qc.cwl
    in:
      title_file: title_file
      inputs_yaml: inputs_yaml
      family_sizes: umi_qc_tables/family_sizes
      family_types_A: umi_qc_tables/family_types_A
      family_types_B: umi_qc_tables/family_types_B

      standard_waltz_metrics_pool_a: standard_aggregate_bam_metrics_pool_a/output_dir
      unfiltered_waltz_metrics_pool_a: unfiltered_aggregate_bam_metrics_pool_a/output_dir
      simplex_waltz_metrics_pool_a: simplex_aggregate_bam_metrics_pool_a/output_dir
      duplex_waltz_metrics_pool_a: duplex_aggregate_bam_metrics_pool_a/output_dir
      standard_waltz_metrics_pool_b: standard_aggregate_bam_metrics_pool_b/output_dir
      unfiltered_waltz_metrics_pool_b: unfiltered_aggregate_bam_metrics_pool_b/output_dir
      simplex_waltz_metrics_pool_b: simplex_aggregate_bam_metrics_pool_b/output_dir
      duplex_waltz_metrics_pool_b: duplex_aggregate_bam_metrics_pool_b/output_dir
    out: [
      read_counts,
      align_rate,
      mean_cov,
      on_target_rate,
      gc_cov_each_sample,
      insert_sizes,
      coverage_per_interval,
      title_page,
      pipeline_inputs,
      family_types,
      family_sizes_all,
      family_sizes_simplex,
      family_sizes_duplex]

  #######################################
  # Combine FP, Noise, & Std qc results #
  #######################################

  combine_qc:
    run: ../../cwl_tools/python/combine_qc_pdfs.cwl
    in:
      title_file: title_file
      read_counts: innovation_qc/read_counts
      align_rate: innovation_qc/align_rate
      mean_cov: innovation_qc/mean_cov
      on_target_rate: innovation_qc/on_target_rate
      gc_cov_each_sample: innovation_qc/gc_cov_each_sample
      insert_sizes: innovation_qc/insert_sizes
      coverage_per_interval: innovation_qc/coverage_per_interval
      title_page: innovation_qc/title_page
      pipeline_inputs: innovation_qc/pipeline_inputs
      family_types: innovation_qc/family_types
      family_sizes_all: innovation_qc/family_sizes_all
      family_sizes_simplex: innovation_qc/family_sizes_simplex
      family_sizes_duplex: innovation_qc/family_sizes_duplex
      noise_alt_percent: duplex_noise_plots_A/noise_alt_percent
      noise_contributing_sites: duplex_noise_plots_A/noise_contributing_sites
      fingerprinting_qc: fingerprinting/FPFigures
      gender_check: fingerprinting/gender_plot
    out:
      [combined_qc]

  ####################
  # Put in Directory #
  ####################

  group_qc_files:
    run: ../../cwl_tools/expression_tools/group_qc_files.cwl
    in:
      standard_pool_a: standard_noise_tables_A/waltz_folder_with_noise
      unfiltered_pool_a: unfiltered_noise_tables_A/waltz_folder_with_noise
      simplex_pool_a: simplex_noise_tables_A/waltz_folder_with_noise
      duplex_pool_a: duplex_noise_tables_A/waltz_folder_with_noise

      standard_pool_b: standard_aggregate_bam_metrics_pool_b/output_dir
      unfiltered_pool_b: unfiltered_aggregate_bam_metrics_pool_b/output_dir
      simplex_pool_b: simplex_aggregate_bam_metrics_pool_b/output_dir
      duplex_pool_b: duplex_aggregate_bam_metrics_pool_b/output_dir

      all_fp_results: fingerprinting/all_fp_results
      gender_table: fingerprinting/gender_table

      family_sizes: umi_qc_tables/family_sizes
      family_types_A: umi_qc_tables/family_types_A
      family_types_B: umi_qc_tables/family_types_B
      combined_qc: combine_qc/combined_qc
    out: [qc_files]
