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
  project_name: string
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

  waltz_standard_a_exon_level_files: Directory
  waltz_unfiltered_a_exon_level_files: Directory
  waltz_simplex_a_exon_level_files: Directory
  waltz_duplex_a_exon_level_files: Directory

outputs:

  combined_qc:
    type: Directory
    outputSource: group_qc_files/qc_files

  tables:
    type: Directory
    outputSource: main_tables_module/tables

steps:

  #############################################
  # Aggregate Bam Metrics across samples      #
  #                                           #
  # For each combination of collapsing method #
  # and pool (8x)                             #
  #                                           #
  # As well as 4x with Exon-level bedfile     #
  #############################################

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

  standard_aggregate_bam_metrics_pool_a_exon_level:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_standard_a_exon_level_files
      output_dir_name:
        valueFrom: $('waltz_standard_a_exon_level)
    out: [output_dir]

  unfiltered_aggregate_bam_metrics_pool_a_exon_level:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_unfiltered_a_exon_level_files
      output_dir_name:
        valueFrom: $('waltz_unfiltered_a_exon_level')
    out: [output_dir]

  simplex_aggregate_bam_metrics_pool_a_exon_level:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_simplex_a_exon_level_files
      output_dir_name:
        valueFrom: $('waltz_simplex_a_exon_level')
    out: [output_dir]

  duplex_aggregate_bam_metrics_pool_a_exon_level:
    run: ../../cwl_tools/python/aggregate_bam_metrics.cwl
    in:
      waltz_input_files: waltz_duplex_a_exon_level_files
      output_dir_name:
        valueFrom: $('waltz_duplex_a_exon_level')
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
    out: [noise_alt_percent, noise_contributing_sites, noise_by_substitution]

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

  main_tables_module:
    run: ../../cwl_tools/python/tables_module.cwl
    in:
      standard_waltz_metrics_pool_a: standard_aggregate_bam_metrics_pool_a/output_dir
      unfiltered_waltz_metrics_pool_a: unfiltered_aggregate_bam_metrics_pool_a/output_dir
      simplex_waltz_metrics_pool_a: simplex_aggregate_bam_metrics_pool_a/output_dir
      duplex_waltz_metrics_pool_a: duplex_aggregate_bam_metrics_pool_a/output_dir
      standard_waltz_metrics_pool_b: standard_aggregate_bam_metrics_pool_b/output_dir
      unfiltered_waltz_metrics_pool_b: unfiltered_aggregate_bam_metrics_pool_b/output_dir
      simplex_waltz_metrics_pool_b: simplex_aggregate_bam_metrics_pool_b/output_dir
      duplex_waltz_metrics_pool_b: duplex_aggregate_bam_metrics_pool_b/output_dir

      standard_waltz_metrics_pool_a_exon_level: standard_aggregate_bam_metrics_pool_a_exon_level/output_dir
      unfiltered_waltz_metrics_pool_a_exon_level: unfiltered_aggregate_bam_metrics_pool_a_exon_level/output_dir
      simplex_waltz_metrics_pool_a_exon_level: simplex_aggregate_bam_metrics_pool_a_exon_level/output_dir
      duplex_waltz_metrics_pool_a_exon_level: duplex_aggregate_bam_metrics_pool_a_exon_level/output_dir
    out: [tables]

  main_plots_module:
    run: ../../cwl_tools/python/plots_module.cwl
    in:
      title_file: title_file
      inputs_yaml: inputs_yaml
      tables: main_tables_module/tables
      family_sizes: umi_qc_tables/family_sizes
      family_types_A: umi_qc_tables/family_types_A
      family_types_B: umi_qc_tables/family_types_B
    out: [
      read_counts,
      align_rate,
      on_target_rate,
      gc_cov_each_sample,
      insert_sizes,
      coverage_per_interval,
      title_page,
      cov_and_family_type_A,
      cov_and_family_type_B,
      family_sizes_all,
      family_sizes_simplex,
      family_sizes_duplex,
      pipeline_inputs,
      coverage_per_interval_exon_level]

  ####################################################
  # Combine FP, Noise, & Std qc result PDFs into one #
  ####################################################

  combine_qc:
    run: ../../cwl_tools/python/combine_qc_pdfs.cwl
    in:
      project_name: project_name
      title_page: main_plots_module/title_page
      read_counts: main_plots_module/read_counts
      align_rate: main_plots_module/align_rate
      on_target_rate: main_plots_module/on_target_rate
      gc_cov_each_sample: main_plots_module/gc_cov_each_sample
      insert_sizes: main_plots_module/insert_sizes
      coverage_per_interval: main_plots_module/coverage_per_interval
      coverage_per_interval_exon_level: main_plots_module/coverage_per_interval_exon_level
      cov_and_family_type_A: main_plots_module/cov_and_family_type_A
      cov_and_family_type_B: main_plots_module/cov_and_family_type_B
      family_sizes_all: main_plots_module/family_sizes_all
      family_sizes_simplex: main_plots_module/family_sizes_simplex
      family_sizes_duplex: main_plots_module/family_sizes_duplex
      noise_alt_percent: duplex_noise_plots_A/noise_alt_percent
      noise_contributing_sites: duplex_noise_plots_A/noise_contributing_sites
      noise_by_substitution: duplex_noise_plots_A/noise_by_substitution
      fingerprinting_qc: fingerprinting/FPFigures
      gender_check: fingerprinting/gender_plot
      pipeline_inputs: main_plots_module/pipeline_inputs
    out: [combined_qc]

  ###################################
  # Put everything in one Directory #
  ###################################

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

      standard_pool_a_exon_level: standard_aggregate_bam_metrics_pool_a_exon_level/output_dir
      unfiltered_pool_a_exon_level: unfiltered_aggregate_bam_metrics_pool_a_exon_level/output_dir
      simplex_pool_a_exon_level: simplex_aggregate_bam_metrics_pool_a_exon_level/output_dir
      duplex_pool_a_exon_level: duplex_aggregate_bam_metrics_pool_a_exon_level/output_dir

      qc_tables: main_tables_module/tables
      all_fp_results: fingerprinting/all_fp_results
      gender_table: fingerprinting/gender_table
      family_sizes: umi_qc_tables/family_sizes
      family_types_A: umi_qc_tables/family_types_A
      family_types_B: umi_qc_tables/family_types_B
      combined_qc: combine_qc/combined_qc
    out: [qc_files]
