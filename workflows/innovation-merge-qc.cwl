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

  standard_waltz_count_reads_files: File[]
  standard_waltz_pileup_metrics_files: File[]

  fulcrum_waltz_count_reads_files: File[]
  fulcrum_waltz_pileup_metrics_files: File[]

outputs:

  qc_report:
    type: File
    outputSource: innovation_qc/qc_pdf

steps:

  #############################################
  # Merge Waltz output (standard and fulcrum) #
  #############################################

  merge_waltz_output_files_standard:
    run: ./innovation-merge-directories/0.0.0/innovation-merge-directories.cwl
    in:
      files_1: standard_waltz_count_reads_files
      files_2: standard_waltz_pileup_metrics_files
    out:
      [output_files]

  merge_waltz_output_files_fulcrum:
    run: ./innovation-merge-directories/0.0.0/innovation-merge-directories.cwl
    in:
      files_1: fulcrum_waltz_count_reads_files
      files_2: fulcrum_waltz_pileup_metrics_files
    out:
      [output_files]


  ################################################
  # Aggregate Bam Metrics (standard and fulcrum) #
  ################################################

  standard_aggregate_bam_metrics:
    run: ./innovation-aggregate-bam-metrics/0.0.0/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: merge_waltz_output_files_standard/output_files
    out:
      [output_dir]

  fulcrum_aggregate_bam_metrics:
    run: ./innovation-aggregate-bam-metrics/0.0.0/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: merge_waltz_output_files_fulcrum/output_files
    out:
      [output_dir]


  #################
  # Innovation-QC #
  #################

  innovation_qc:
    run: ./innovation-qc/0.0.0/innovation-qc.cwl
    in:
      standard_waltz_metrics: standard_aggregate_bam_metrics/output_dir
      fulcrum_waltz_metrics: fulcrum_aggregate_bam_metrics/output_dir
      title_file: title_file
    out:
      [qc_pdf]
