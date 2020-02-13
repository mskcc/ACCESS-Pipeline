cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/collapsing_tools.yaml
      - $import: ../../resources/schemas/params/waltz.yaml

inputs:
  run_tools: ../../resources/schemas/collapsing_tools.yaml#run_tools
  waltz__params: ../../resources/schemas/params/waltz.yaml#waltz__params

  project_name: string
  title_file: File
  inputs_yaml: File

  sample_id: string[]
  patient_id: string[]
  sample_class: string[]
  standard_bams: File[]
  marianas_unfiltered_bams: File[]
  marianas_simplex_bams: File[]
  marianas_duplex_bams: File[]
  sample_directories: Directory[]

  A_on_target_positions: File
  B_on_target_positions: File
  noise__good_positions_A: File
  pool_a_bed_file: File
  pool_b_bed_file: File
  pool_a_bed_file_exonlevel: File
  gene_list: File
  reference_fasta: string
  reference_fasta_fai: string
  FP_config_file: File
  hotspots: File

outputs:

  combined_qc:
    type: Directory
    outputSource: qc_workflow_wo_waltz/combined_qc

  tables:
    type: Directory
    outputSource: qc_workflow_wo_waltz/tables

  picard_qc:
    type: Directory
    outputSource: aggregate_picard_metrics/combined

  hotspots_in_normals_data:
    type: File
    outputSource: qc_workflow_wo_waltz/hotspots_in_normals_data

steps:

  ##############
  # Waltz Runs #
  ##############

  waltz_workflow:
    run: ../waltz/waltz_workflow_all_bams.cwl
    in:
      title_file: title_file
      run_tools: run_tools
      waltz__params: waltz__params
      pool_a_bed_file: pool_a_bed_file
      pool_b_bed_file: pool_b_bed_file
      pool_a_bed_file_exonlevel: pool_a_bed_file_exonlevel
      gene_list: gene_list
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      standard_bams: standard_bams
      marianas_unfiltered_bams: marianas_unfiltered_bams
      marianas_simplex_bams: marianas_simplex_bams
      marianas_duplex_bams: marianas_duplex_bams
    out: [
      waltz_standard_pool_a_files,
      waltz_unfiltered_pool_a_files,
      waltz_simplex_pool_a_files,
      waltz_duplex_pool_a_files,
      waltz_standard_pool_b_files,
      waltz_unfiltered_pool_b_files,
      waltz_simplex_pool_b_files,
      waltz_duplex_pool_b_files,
      waltz_standard_a_exon_level_files,
      waltz_unfiltered_a_exon_level_files,
      waltz_simplex_a_exon_level_files,
      waltz_duplex_a_exon_level_files,
      waltz_unfiltered_pool_a_pileups,
      waltz_duplex_pool_a_pileups]

  #################################
  # Picard for additional metrics #
  #################################

  collect_multiple_metrics:
    run: ../../cwl_tools/picard/CollectMultipleMetrics.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_8)
      picard:
        valueFrom: $(inputs.run_tools.picard_path)
      input_bam: standard_bams
      output_name:
        valueFrom: $(inputs.input_bam.basename)
      program:
        valueFrom: |
          ${
            return [
              'CollectAlignmentSummaryMetrics',
              'CollectInsertSizeMetrics',
              'QualityScoreDistribution',
              'MeanQualityByCycle'
            ]
          }
    out: [all_metrics, qual_file, qual_hist, is_file, is_hist]
    scatter: input_bam
    scatterMethod: dotproduct

  aggregate_picard_metrics:
    run: ../../cwl_tools/expression_tools/combine_files_from_directories.cwl
    in:
      output_directory_name:
        valueFrom: $('picard_metrics')
      directories: collect_multiple_metrics/all_metrics
    out: [combined]

  #########################
  # QC workflow W/O Waltz #
  #########################

  qc_workflow_wo_waltz:
    run: ./qc_workflow_wo_waltz.cwl
    in:
      run_tools: run_tools
      project_name: project_name
      title_file: title_file
      inputs_yaml: inputs_yaml
      FP_config_file: FP_config_file
      sample_directories: sample_directories
      A_on_target_positions: A_on_target_positions
      B_on_target_positions: B_on_target_positions
      noise__good_positions_A: noise__good_positions_A
      hotspots: hotspots

      sample_id: sample_id
      patient_id: patient_id
      sample_class: sample_class
      waltz_unfiltered_pool_a_pileups: waltz_workflow/waltz_unfiltered_pool_a_pileups
      waltz_duplex_pool_a_pileups: waltz_workflow/waltz_duplex_pool_a_pileups

      picard_metrics: aggregate_picard_metrics/combined

      waltz_standard_pool_a: waltz_workflow/waltz_standard_pool_a_files
      waltz_unfiltered_pool_a: waltz_workflow/waltz_unfiltered_pool_a_files
      waltz_simplex_pool_a: waltz_workflow/waltz_simplex_pool_a_files
      waltz_duplex_pool_a: waltz_workflow/waltz_duplex_pool_a_files
      waltz_standard_pool_b: waltz_workflow/waltz_standard_pool_b_files
      waltz_unfiltered_pool_b: waltz_workflow/waltz_unfiltered_pool_b_files
      waltz_simplex_pool_b: waltz_workflow/waltz_simplex_pool_b_files
      waltz_duplex_pool_b: waltz_workflow/waltz_duplex_pool_b_files

      waltz_standard_a_exon_level_files: waltz_workflow/waltz_standard_a_exon_level_files
      waltz_unfiltered_a_exon_level_files: waltz_workflow/waltz_unfiltered_a_exon_level_files
      waltz_simplex_a_exon_level_files: waltz_workflow/waltz_simplex_a_exon_level_files
      waltz_duplex_a_exon_level_files: waltz_workflow/waltz_duplex_a_exon_level_files
    out: [
      combined_qc,
      tables,
      hotspots_in_normals_data]
