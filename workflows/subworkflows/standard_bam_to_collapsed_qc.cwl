cwlVersion: v1.0

class: Workflow

doc: |
  This is a workflow to go from standard bams to collapsed bams and QC results.

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/collapsing_tools.yaml
      - $import: ../../resources/schemas/params/abra.yaml
      - $import: ../../resources/schemas/params/waltz.yaml
      - $import: ../../resources/schemas/params/marianas_collapsing.yaml
      - $import: ../../resources/schemas/params/fix_mate_information.yaml
      - $import: ../../resources/schemas/params/find_covered_intervals.yaml
      - $import: ../../resources/schemas/params/add_or_replace_read_groups.yaml

inputs:

  run_tools: ../../resources/schemas/collapsing_tools.yaml#run_tools
  abra__params: ../../resources/schemas/params/abra.yaml#abra__params
  waltz__params: ../../resources/schemas/params/waltz.yaml#waltz__params
  add_or_replace_read_groups__params: ../../resources/schemas/params/add_or_replace_read_groups.yaml#add_or_replace_read_groups__params
  find_covered_intervals__params: ../../resources/schemas/params/find_covered_intervals.yaml#find_covered_intervals__params
  fix_mate_information__params: ../../resources/schemas/params/fix_mate_information.yaml#fix_mate_information__params
  marianas_collapsing__params: ../../resources/schemas/params/marianas_collapsing.yaml#marianas_collapsing__params

  # Standard Bams
  standard_bams:
    type: File[]
    secondaryFiles: [^.bai]
  title_file: File
  inputs_yaml: File
  project_name: string

  patient_id: string[]
  sample_class: string[]
  add_rg_LB: int[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]

  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file?
  # so we need to use strings here instead of file types
  reference_fasta: string
  reference_fasta_fai: string
  fci_2__basq_fix: boolean?
  pool_a_bed_file: File
  pool_b_bed_file: File
  pool_a_bed_file_exonlevel: File
  A_on_target_positions: File
  B_on_target_positions: File
  noise__good_positions_A: File
  gene_list: File
  FP_config_file: File
  hotspots: File

outputs:

  bam_dirs:
    type: Directory[]
    outputSource: make_bam_output_directories/directory

  unfiltered_bams:
    type: File[]
    outputSource: flatten_array_bams/output_bams

  simplex_bams:
    type: File[]
    outputSource: separate_bams/simplex_bam

  duplex_bams:
    type: File[]
    outputSource: separate_bams/duplex_bam

  combined_qc:
    type: Directory
    outputSource: qc_workflow/combined_qc

  qc_tables:
    type: Directory
    outputSource: qc_workflow/tables

  picard_qc:
    type: Directory
    outputSource: qc_workflow/picard_qc

  hotspots_in_normals_data:
    type: File
    outputSource: qc_workflow/hotspots_in_normals_data

steps:

  ##############################
  # Get pileups for collapsing #
  ##############################

- id: waltz_standard_pool_a
  run: ../waltz/waltz-workflow.cwl
  in:
    run_tools: run_tools
    waltz__params: waltz__params
    input_bam: standard_bams
    bed_file: pool_a_bed_file
    gene_list: gene_list
    reference_fasta: reference_fasta
    reference_fasta_fai: reference_fasta_fai
  out: [pileup, waltz_output_files]
  scatter: [input_bam]
  scatterMethod: dotproduct

  #####################
  # Collapse Std Bams #
  #####################

- id: umi_collapsing
  run: ../marianas/marianas_collapsing_workflow.cwl
  in:
    run_tools: run_tools
    reference_fasta: reference_fasta
    reference_fasta_fai: reference_fasta_fai
    marianas_collapsing__params: marianas_collapsing__params
    add_or_replace_read_groups__params: add_or_replace_read_groups__params

    input_bam: standard_bams
    pileup: waltz_standard_pool_a/pileup

    add_rg_LB: add_rg_LB
    add_rg_ID: add_rg_ID
    add_rg_PU: add_rg_PU
    add_rg_SM: add_rg_SM
    add_rg_PL:
      valueFrom: $(inputs.add_or_replace_read_groups__params.add_rg_PL)
    add_rg_CN:
      valueFrom: $(inputs.add_or_replace_read_groups__params.add_rg_CN)

  out: [
    collapsed_bams,
    first_pass_output_file,
    first_pass_alt_allele,
    first_pass_alt_allele_sorted,
    second_pass_alt_alleles,
    collapsed_fastq_1,
    collapsed_fastq_2,
    first_pass_insertions,
    second_pass_insertions
  ]
  scatter: [
    input_bam,
    pileup,
    add_rg_LB,
    add_rg_ID,
    add_rg_PU,
    add_rg_SM]
  scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
  # and run Abra a 2nd time  #
  ############################

- id: group_bams_by_patient
  run: ../../cwl_tools/expression_tools/group_bams.cwl
  in:
    bams: umi_collapsing/collapsed_bams
    patient_ids: patient_id
  out:
    [grouped_bams, grouped_patient_ids]

- id: abra_workflow
  run: ../ABRA/abra_workflow.cwl
  in:
    run_tools: run_tools
    reference_fasta: reference_fasta
    bams: group_bams_by_patient/grouped_bams
    patient_id: group_bams_by_patient/grouped_patient_ids

    fci__basq_fix: fci_2__basq_fix
    find_covered_intervals__params: find_covered_intervals__params
    abra__params: abra__params
    fix_mate_information__params: fix_mate_information__params
  out: [ir_bams]
  scatter: [bams, patient_id]
  scatterMethod: dotproduct

  ################################
  # Return to flat array of bams #
  ################################

- id: flatten_array_bams
  run: ../../cwl_tools/expression_tools/flatten_array_bam.cwl
  in:
    bams: abra_workflow/ir_bams
  out: [output_bams]

  ################
  # SeparateBams #
  ################

- id: separate_bams
  run: ../../cwl_tools/marianas/SeparateBams.cwl
  in:
    run_tools: run_tools
    java_8:
      valueFrom: ${return inputs.run_tools.java_8}
    marianas_path:
      valueFrom: ${return inputs.run_tools.marianas_path}
    collapsed_bam: flatten_array_bams/output_bams
  out: [simplex_bam, duplex_bam]
  scatter: [collapsed_bam]
  scatterMethod: dotproduct

  ##################################
  # Make sample output directories #
  ##################################

- id: make_bam_output_directories
  run: ../../cwl_tools/expression_tools/make_sample_output_dirs.cwl
  in:
    sample_id: add_rg_ID
    r1_fastq: umi_collapsing/collapsed_fastq_1
    r2_fastq: umi_collapsing/collapsed_fastq_2
    first_pass_file: umi_collapsing/first_pass_output_file
    first_pass_insertions: umi_collapsing/first_pass_insertions
    second_pass_insertions: umi_collapsing/second_pass_insertions
    first_pass_sorted: umi_collapsing/first_pass_alt_allele_sorted
    first_pass_alt_alleles: umi_collapsing/first_pass_alt_allele
    second_pass: umi_collapsing/second_pass_alt_alleles
  scatter: [
    sample_id,
    r1_fastq,
    r2_fastq,
    first_pass_file,
    first_pass_sorted,
    first_pass_alt_alleles,
    first_pass_insertions,
    second_pass_insertions,
    second_pass]
  scatterMethod: dotproduct
  out: [directory]

  ######
  # QC #
  ######

- id: qc_workflow
  run: ../QC/qc_workflow.cwl
  in:
    run_tools: run_tools
    waltz__params: waltz__params

    project_name: project_name
    title_file: title_file
    sample_directories: make_bam_output_directories/directory
    A_on_target_positions: A_on_target_positions
    B_on_target_positions: B_on_target_positions
    noise__good_positions_A: noise__good_positions_A
    inputs_yaml: inputs_yaml
    pool_a_bed_file: pool_a_bed_file
    pool_b_bed_file: pool_b_bed_file
    pool_a_bed_file_exonlevel: pool_a_bed_file_exonlevel
    gene_list: gene_list
    reference_fasta: reference_fasta
    reference_fasta_fai: reference_fasta_fai
    hotspots: hotspots

    sample_id: add_rg_ID
    patient_id: patient_id
    sample_class: sample_class
    standard_bams: standard_bams
    # Collapsed, and after 2nd Indel Realignment:
    marianas_unfiltered_bams: flatten_array_bams/output_bams
    marianas_simplex_bams: separate_bams/simplex_bam
    marianas_duplex_bams: separate_bams/duplex_bam
    FP_config_file: FP_config_file
  out: [
    picard_qc,
    combined_qc,
    tables,
    hotspots_in_normals_data]