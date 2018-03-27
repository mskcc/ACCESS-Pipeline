#!/usr/bin/env cwl-runner

$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/
  doap: http://usefulinc.com/ns/doap#

$schemas:
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf
- http://usefulinc.com/ns/doap#

doap:release:
- class: doap:Version
  doap:name: innovation_pipeline.scatter
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 0.0.0

dct:creator:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsoni@mskcc.org

dct:contributor:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsoni@mskcc.org

cwlVersion: v1.0

class: Workflow

doc: |
  This is the top-level workflow that includes all sub-workflow modules:

  Module 0:
    UMI Clipping

  Module 1:
    Trimming
    Mapping
    Replacing Read Groups
    Marking Duplicates

  Module 2:
    Indel Realignment
    Fix Mate Information
    Base Quality Score Recalibration

  Module 2.5 (So-named to fit with Roslin names):
    UMI Family Collapsing with Marianas
    UMI Family Collapsing with Fulcrum


requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:

  title_file: File
  fastq1: File[]
  fastq2: File[]
  sample_sheet: File[]
  patient_id: string[]

  reference_fasta: string
  reference_fasta_fai: string

  # Marianas Clipping
  umi_length: int
  output_project_folder: string

  # Module 1
  adapter: string[]
  adapter2: string[]
  add_rg_PL: string
  add_rg_CN: string
  add_rg_LB: int[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]

  md__assume_sorted: boolean
  md__compression_level: int
  md__create_index: boolean
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string

  # Module 2
  fci__minbq: int
  fci__minmq: int
  fci__cov: int
  fci__rf: string
  abra__kmers: string
  abra__scratch: string
  abra__mad: int

  fix_mate_information__sort_order: string
  fix_mate_information__validation_stringency: string
  fix_mate_information__compression_level: int
  fix_mate_information__create_index: boolean

  bqsr__nct: int
  bqsr__knownSites_dbSNP: File
  bqsr__knownSites_millis: File
  bqsr__rf: string

  print_reads__nct: int
  print_reads__EOQ: boolean
  print_reads__baq: string

  # Fulcrum
  tmp_dir: string
  fulcrum__sort_order: string
  fulcrum__grouping_strategy: string
  fulcrum__min_mapping_quality: int
  fulcrum__tag_family_size_counts_output: string
  fulcrum__call_duplex_min_reads: string
  fulcrum__filter_min_base_quality: int
  fulcrum__filter_min_reads__simplex_duplex: string
  fulcrum__filter_min_reads__duplex: string

  # Marianas
  marianas__mismatches: int
  marianas__wobble: int
  marianas__min_consensus_percent: int
  marianas_collapsing__outdir: string

  # Waltz
  coverage_threshold: int
  gene_list: File
  bed_file: File
  waltz__min_mapping_quality: int

outputs:

  standard_bams:
    type:
      type: array
      items: File
    outputSource: flatten_array_bams/output_bams

  ###########
  # Fulcrum #
  ###########

  fulcrum_simplex_duplex_bams:
    type:
      type: array
      items: File
    outputSource: umi_collapsing/fulcrum_simplex_duplex_bams

  fulcrum_duplex_bams:
    type:
      type: array
      items: File
    outputSource: umi_collapsing/fulcrum_duplex_bams

  duplex_seq_metrics:
    type:
      type: array
      items: File
    outputSource: umi_collapsing/duplex_seq_metrics

  ############
  # Marianas #
  ############

  marianas_simplex_duplex_bams:
    type:
      type: array
      items: File
    outputSource: umi_collapsing/marianas_simplex_duplex_bams

  marianas_duplex_bams:
    type:
      type: array
      items: File
    outputSource: umi_collapsing/marianas_duplex_bams

  ##############
  # QC reports #
  ##############

  duplex_qc_report:
    type: File[]
    outputSource: collapsed_qc_step/duplex_qc_pdf

steps:

  #########################
  # Marianas UMI Clipping #
  #########################

  umi_clipping:
    run: ../cwl_tools/marianas/ProcessLoopUMIFastq.cwl
    in:
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      umi_length: umi_length
      output_project_folder: output_project_folder
    out: [processed_fastq_1, processed_fastq_2, info, output_sample_sheet, umi_frequencies]
    scatter: [fastq1, fastq2, sample_sheet]
    scatterMethod: dotproduct

  ####################
  # Adapted Module 1 #
  ####################

  module_1_innovation:
    run: ./module-1.cwl
    in:
      tmp_dir: tmp_dir
      fastq1: umi_clipping/processed_fastq_1
      fastq2: umi_clipping/processed_fastq_2
      adapter: adapter
      adapter2: adapter2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN

      md__assume_sorted: md__assume_sorted
      md__compression_level: md__compression_level
      md__create_index: md__create_index
      md__validation_stringency: md__validation_stringency
      md__duplicate_scoring_strategy: md__duplicate_scoring_strategy

      bed_file: bed_file
      # Todo: This could be easier to find
      output_suffix:
        valueFrom: ${ return '_aln' }
    out: [bam, bai, md_metrics]
    scatter: [fastq1, fastq2, adapter, adapter2, add_rg_LB, add_rg_ID, add_rg_PU, add_rg_SM]
    scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
  ############################

  group_bams_by_patient:
    run: ../cwl_tools/expression_tools/group_bams.cwl
    in:
      bams: module_1_innovation/bam
      patient_ids: patient_id
    out:
      [grouped_bams, grouped_patient_ids]

  ####################
  # Adapted Module 2 #
  ####################

  module_2:
    run: ./module-2.cwl
    in:
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta

      bams: group_bams_by_patient/grouped_bams
      patient_id: group_bams_by_patient/grouped_patient_ids

      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__cov: fci__cov
      fci__rf: fci__rf
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      abra__mad: abra__mad
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__create_index: fix_mate_information__create_index
      bqsr__nct: bqsr__nct
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      bqsr__rf: bqsr__rf
      print_reads__nct: print_reads__nct
      print_reads__EOQ: print_reads__EOQ
      print_reads__baq: print_reads__baq

    out: [standard_bams, standard_bais, covint_list, covint_bed]
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

  #############################
  # Waltz Run (Standard Bams) #
  #############################

  waltz_standard:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: flatten_array_bams/output_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  ##################
  # UMI Collapsing #
  ##################

  umi_collapsing:
    run: ./module-2.5.cwl
    in:
      bam: flatten_array_bams/output_bams
      title_file: title_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      # Arrg
      add_rg_PL: add_rg_PL
      add_rg_CN: add_rg_CN
      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM

      # Fulcrum
      tmp_dir: tmp_dir
      fulcrum__sort_order: fulcrum__sort_order
      fulcrum__grouping_strategy: fulcrum__grouping_strategy
      fulcrum__min_mapping_quality: fulcrum__min_mapping_quality
      fulcrum__tag_family_size_counts_output: fulcrum__tag_family_size_counts_output
      fulcrum__call_duplex_min_reads: fulcrum__call_duplex_min_reads
      fulcrum__filter_min_base_quality: fulcrum__filter_min_base_quality
      fulcrum__filter_min_reads__simplex_duplex: fulcrum__filter_min_reads__simplex_duplex
      fulcrum__filter_min_reads__duplex: fulcrum__filter_min_reads__duplex

      # Marianas
      marianas__mismatches: marianas__mismatches
      marianas__wobble: marianas__wobble
      marianas__min_consensus_percent: marianas__min_consensus_percent
      marianas_collapsing__outdir: marianas_collapsing__outdir

      standard_pileup: waltz_standard/pileup

    out: [
      fulcrum_simplex_duplex_bams,
      fulcrum_duplex_bams,
      duplex_seq_metrics,
      marianas_simplex_duplex_bams,
      marianas_duplex_bams
    ]

    scatter: [bam, standard_pileup, add_rg_LB, add_rg_ID, add_rg_PU, add_rg_SM]
    scatterMethod: dotproduct

  ##############################
  # Waltz Run (Collapsed Bams) #
  ##############################

  waltz_fulcrum_simplex_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: umi_collapsing/fulcrum_simplex_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_fulcrum_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: umi_collapsing/fulcrum_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_marianas_simplex_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: umi_collapsing/marianas_simplex_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_marianas_duplex:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: umi_collapsing/marianas_duplex_bams
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  #################
  # Innovation-QC #
  #################

  collapsed_qc_step:
    run: ./QC/qc_workflow.cwl
    in:
      title_file: title_file
      standard_waltz_files: waltz_standard/waltz_output_files
      fulcrum_simplex_duplex_waltz_files: waltz_fulcrum_simplex_duplex/waltz_output_files
      fulcrum_duplex_waltz_files: waltz_fulcrum_duplex/waltz_output_files
      marianas_simplex_duplex_waltz_files: waltz_marianas_simplex_duplex/waltz_output_files
      marianas_duplex_waltz_files: waltz_marianas_duplex/waltz_output_files
    out: [duplex_qc_pdf] #simplex_duplex_qc_pdf,
