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
  doap:revision: 1.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 1.0.0

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
requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  title_file: File

  fastq1: string[]
  fastq2: string[]
  sample_sheet: File[]

  umi_length: string
  output_project_folder: string
  outdir: string

  adapter: string[]
  adapter2: string
  genome: string
  add_rg_PL: string
  add_rg_CN: string
  tmp_dir: string

#  bwa_output: string[]
  add_rg_LB: string[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]

  tmp_dir: string
  sort_order: string
  grouping_strategy: string
  min_mapping_quality: string
  tag_family_size_counts_output: string
  reference_fasta: File
  filter_min_reads: string
  filter_min_base_quality: string

  coverage_threshold: string
  gene_list: string
  bed_file: string
  min_mapping_quality: string
  waltz_reference_fasta: string
  waltz_reference_fasta_fai: string


outputs:

  standard_bams:
    type:
      type: array
      items: File
    outputSource: scatter_step/standard_bams

  fulcrum_bams:
    type:
      type: array
      items: File
    outputSource: scatter_step/fulcrum_bams

#  standard_aggregated_waltz_output:
#    type: Directory
#    outputSource: standard_aggregate_bam_metrics/output_dir
#
#  fulcrum_aggregated_waltz_output:
#    type: Directory
#    outputSource: fulcrum_aggregate_bam_metrics/output_dir

  qc_report:
    type: File
    outputSource: innovation_qc/qc_pdf

steps:

  scatter_step:
    run: ./innovation_pipeline.scatter.cwl

    in:
      title_file: title_file

      fastq1: fastq1
      fastq2: fastq2
      sample_sheet: sample_sheet
      umi_length: umi_length
      output_project_folder: output_project_folder
      outdir: outdir
      adapter: adapter
      adapter2: adapter2

      genome: genome
      add_rg_PL: add_rg_PL
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM

      tmp_dir: tmp_dir
      sort_order: sort_order
      grouping_strategy: grouping_strategy
      min_mapping_quality: min_mapping_quality
      tag_family_size_counts_output: tag_family_size_counts_output
      reference_fasta: reference_fasta
      filter_min_reads: filter_min_reads
      filter_min_base_quality: filter_min_base_quality

      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      min_mapping_quality: min_mapping_quality
      waltz_reference_fasta: waltz_reference_fasta
      waltz_reference_fasta_fai: waltz_reference_fasta_fai

    # I7 adapter is different for each sample, I5 is not
    scatter: [adapter,fastq1,fastq2,sample_sheet,add_rg_LB,add_rg_ID,add_rg_PU,add_rg_SM]

    scatterMethod: dotproduct

    out: [
      standard_bams,
      fulcrum_bams,
      output_sample_sheet,
      standard_waltz_files,
#      marianas_waltz_files,
      fulcrum_waltz_files
    ]


  standard_consolidate_bam_metrics:
    run: ./innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: scatter_step/standard_waltz_files
    out:
      [waltz_files]

  fulcrum_consolidate_bam_metrics:
    run: ./innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: scatter_step/fulcrum_waltz_files
    out:
      [waltz_files]


  ################################################
  # Aggregate Bam Metrics (standard and fulcrum) #
  ################################################

  standard_aggregate_bam_metrics:
    run: ./innovation-aggregate-bam-metrics/0.0.0/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: standard_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

#  marianas_aggregate_bam_metrics:
#    run: ./innovation-aggregate-bam-metrics/0.0.0/innovation-aggregate-bam-metrics.cwl
#    in:
#      waltz_input_files: scatter_step/marianas_waltz_files
#    out:
#      [output_dir]

  fulcrum_aggregate_bam_metrics:
    run: ./innovation-aggregate-bam-metrics/0.0.0/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: fulcrum_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]


  #################
  # Innovation-QC #
  #################

  innovation_qc:
    run: ./innovation-qc/0.0.0/innovation-qc.cwl
    in:
      standard_waltz_metrics: standard_aggregate_bam_metrics/output_dir
#      marianas_waltz_metrics: marianas_aggregate_bam_metrics/output_dir
      fulcrum_waltz_metrics: fulcrum_aggregate_bam_metrics/output_dir
      title_file: title_file
    out:
      [qc_pdf]
