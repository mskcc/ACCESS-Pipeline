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

  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file?
  # so we need to use strings here instead of file types
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
  fci__intervals: string[]

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
  bed_file: File
  gene_list: File
  coverage_threshold: int
  waltz__min_mapping_quality: int

outputs:

  standard_bams:
    type:
      type: array
      items: File
    outputSource: standard_bam_generation/standard_bams

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

  standard_bam_generation:
    run: ./standard_pipeline.cwl
    in:
      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      # Process Loop Umi Fastq
      umi_length: umi_length
      output_project_folder: output_project_folder
      # Module 1
      tmp_dir: tmp_dir
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
      md__create_index: md__create_index
      md__assume_sorted: md__assume_sorted
      md__compression_level: md__compression_level
      md__validation_stringency: md__validation_stringency
      md__duplicate_scoring_strategy: md__duplicate_scoring_strategy
      bed_file: bed_file
      # Group bams by patient
      patient_id: patient_id
      # Module 2
      reference_fasta: reference_fasta
      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__cov: fci__cov
      fci__rf: fci__rf
      fci__intervals: fci__intervals
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      abra__mad: abra__mad
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__create_index: fix_mate_information__create_index
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      bqsr__nct: bqsr__nct
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      bqsr__rf: bqsr__rf
      print_reads__nct: print_reads__nct
      print_reads__EOQ: print_reads__EOQ
      print_reads__baq: print_reads__baq
    out: [standard_bams]

  # Todo: this currently gets run 2x
  waltz_standard:
    run: ./waltz/waltz-workflow.cwl
    in:
      input_bam: standard_bam_generation/standard_bams
      bed_file: bed_file
      gene_list: gene_list
      coverage_threshold: coverage_threshold
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
    run: ./module-2_5.cwl
    in:
      tmp_dir: tmp_dir
      bam: standard_bam_generation/standard_bams
      title_file: title_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_PL: add_rg_PL
      add_rg_CN: add_rg_CN
      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      fulcrum__sort_order: fulcrum__sort_order
      fulcrum__grouping_strategy: fulcrum__grouping_strategy
      fulcrum__min_mapping_quality: fulcrum__min_mapping_quality
      fulcrum__tag_family_size_counts_output: fulcrum__tag_family_size_counts_output
      fulcrum__call_duplex_min_reads: fulcrum__call_duplex_min_reads
      fulcrum__filter_min_base_quality: fulcrum__filter_min_base_quality
      fulcrum__filter_min_reads__simplex_duplex: fulcrum__filter_min_reads__simplex_duplex
      fulcrum__filter_min_reads__duplex: fulcrum__filter_min_reads__duplex
      marianas__wobble: marianas__wobble
      marianas__mismatches: marianas__mismatches
      marianas_collapsing__outdir: marianas_collapsing__outdir
      marianas__min_consensus_percent: marianas__min_consensus_percent
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

  #########################
  # QC (Each set of Bams) #
  #########################

  collapsed_qc_step:
    run: ./QC/qc_workflow.cwl
    in:
      title_file: title_file
      bed_file: bed_file
      gene_list: gene_list
      coverage_threshold: coverage_threshold
      waltz__min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      standard_bams: standard_bam_generation/standard_bams
      fulcrum_simplex_duplex_bams: umi_collapsing/fulcrum_simplex_duplex_bams
      fulcrum_duplex_bams: umi_collapsing/fulcrum_duplex_bams
      marianas_simplex_duplex_bams: umi_collapsing/marianas_simplex_duplex_bams
      marianas_duplex_bams: umi_collapsing/marianas_duplex_bams
    out: [duplex_qc_pdf] #simplex_duplex_qc_pdf,
