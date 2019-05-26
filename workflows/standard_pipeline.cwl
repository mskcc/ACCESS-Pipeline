cwlVersion: v1.0

class: Workflow

doc: |
  This is a workflow to go from UMI-tagged fastqs to standard bams.
  It does not include collapsing, or QC
  It does include modules 1 and 2

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_tools/schemas.yaml
      - $import: ../resources/run_params/schemas/process_loop_umi_fastq.yaml
      - $import: ../resources/run_params/schemas/trimgalore.yaml
      - $import: ../resources/run_params/schemas/add_or_replace_read_groups.yaml
      - $import: ../resources/run_params/schemas/mark_duplicates.yaml
      - $import: ../resources/run_params/schemas/find_covered_intervals.yaml
      - $import: ../resources/run_params/schemas/abra.yaml
      - $import: ../resources/run_params/schemas/fix_mate_information.yaml
      - $import: ../resources/run_params/schemas/base_recalibrator.yaml
      - $import: ../resources/run_params/schemas/print_reads.yaml

inputs:
  run_tools: ../resources/run_tools/schemas.yaml#run_tools

  fastq1: File[]
  fastq2: File[]
  sample_sheet: File[]
  patient_id: string[]
  adapter: string[]
  adapter2: string[]
  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file,
  # so we need to use strings here instead of file types
  reference_fasta: string
  reference_fasta_fai: string

  add_rg_LB: int[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]

  bqsr__knownSites_dbSNP: File
  bqsr__knownSites_millis: File

  process_loop_umi_fastq__params: ../resources/run_params/schemas/process_loop_umi_fastq.yaml#process_loop_umi_fastq__params
  trimgalore__params: ../resources/run_params/schemas/trimgalore.yaml#trimgalore__params
  add_or_replace_read_groups__params: ../resources/run_params/schemas/add_or_replace_read_groups.yaml#add_or_replace_read_groups__params
  mark_duplicates__params: ../resources/run_params/schemas/mark_duplicates.yaml#mark_duplicates__params
  find_covered_intervals__params: ../resources/run_params/schemas/find_covered_intervals.yaml#find_covered_intervals__params
  abra__params: ../resources/run_params/schemas/abra.yaml#abra__params
  fix_mate_information__params: ../resources/run_params/schemas/fix_mate_information.yaml#fix_mate_information__params
  base_recalibrator__params: ../resources/run_params/schemas/base_recalibrator.yaml#base_recalibrator__params
  print_reads__params: ../resources/run_params/schemas/print_reads.yaml#print_reads__params

outputs:

  standard_bams:
    type: File[]
    outputSource: flatten_array_bams/output_bams

  clipping_dirs:
    type: Directory[]
    outputSource: umi_clipping/clipping_dir

  clipping_info:
    type: File[]
    outputSource: umi_clipping/clipping_info

  clstats1:
    type: File[]
    outputSource: module_1/clstats1

  clstats2:
    type: File[]
    outputSource: module_1/clstats2

  md_metrics:
    type: File[]
    outputSource: module_1/md_metrics

  covint_list:
    type: File[]
    outputSource: module_2/covint_list

  covint_bed:
    type: File[]
    outputSource: module_2/covint_bed

steps:

  #########################
  # Marianas UMI Clipping #
  #########################

  umi_clipping:
    run: ../cwl_tools/marianas/ProcessLoopUMIFastq.cwl
    in:
      run_tools: run_tools
      params: process_loop_umi_fastq__params
      java_8:
        valueFrom: $(inputs.run_tools.java_8)
      marianas_path:
        valueFrom: $(inputs.run_tools.marianas_path)
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      add_rg_SM: add_rg_SM
      umi_length:
        valueFrom: $(inputs.params.umi_length)
      output_project_folder:
        valueFrom: $(inputs.params.output_project_folder)

    out: [
      processed_fastq_1,
      processed_fastq_2,
      clipping_info,
      clipping_dir]
    scatter: [fastq1, fastq2, sample_sheet, add_rg_SM]
    scatterMethod: dotproduct

  ####################
  # Adapted Module 1 #
  ####################

  module_1:
    run: ./module-1.cwl
    in:
      run_tools: run_tools
      fastq1: umi_clipping/processed_fastq_1
      fastq2: umi_clipping/processed_fastq_2
      adapter: adapter
      adapter2: adapter2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN:
        valueFrom: $(inputs.add_or_replace_read_groups__params.add_rg_CN)
      add_rg_PL:
        valueFrom: $(inputs.add_or_replace_read_groups__params.add_rg_PL)

      trimgalore__params: trimgalore__params
      add_or_replace_read_groups__params: add_or_replace_read_groups__params
      mark_duplicates__params: mark_duplicates__params
    out: [bam, bai, clstats1, clstats2, md_metrics]
    scatter: [fastq1, fastq2, add_rg_LB, add_rg_ID, add_rg_PU, add_rg_SM, adapter, adapter2]
    scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
  ############################

  group_bams_by_patient:
    run: ../cwl_tools/expression_tools/group_bams.cwl
    in:
      bams: module_1/bam
      patient_ids: patient_id
    out:
      [grouped_bams, grouped_patient_ids]

  ####################
  # Adapted Module 2 #
  ####################

  module_2:
    run: ./module-2.cwl
    in:
      run_tools: run_tools
      reference_fasta: reference_fasta
      bams: group_bams_by_patient/grouped_bams
      patient_id: group_bams_by_patient/grouped_patient_ids

      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis

      find_covered_intervals__params: find_covered_intervals__params
      abra__params: abra__params
      fix_mate_information__params: fix_mate_information__params
      base_recalibrator__params: base_recalibrator__params
      print_reads__params: print_reads__params

    out: [standard_bams, covint_list, covint_bed]
    scatter: [bams, patient_id]
    scatterMethod: dotproduct

  ################################
  # Return to flat array of bams #
  ################################

  flatten_array_bams:
    run: ../cwl_tools/expression_tools/flatten_array_bam.cwl
    in:
      bams: module_2/standard_bams
    out: [output_bams]
