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
  doap:name: qc_workflow
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

requirements:
  MultipleInputFeatureRequirement: {}

inputs:

  title_file: File

  standard_waltz_files:
    type:
      type: array
      items:
        type: array
        items: File
  fulcrum_simplex_duplex_waltz_files:
    type:
      type: array
      items:
        type: array
        items: File
  fulcrum_duplex_waltz_files:
    type:
      type: array
      items:
        type: array
        items: File
  marianas_simplex_duplex_waltz_files:
    type:
      type: array
      items:
        type: array
        items: File
  marianas_duplex_waltz_files:
    type:
      type: array
      items:
        type: array
        items: File

outputs:

  simplex_duplex_qc_pdf:
    type: File
    outputSource: simplex_duplex_innovation_qc/qc_pdf

  duplex_qc_pdf:
    type: File
    outputSource: duplex_innovation_qc/qc_pdf

steps:

  standard_consolidate_bam_metrics:
    run: ../../cwl_tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: standard_waltz_files
    out:
      [waltz_files]

  fulcrum_simplex_duplex_consolidate_bam_metrics:
    run: ../../cwl_tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: fulcrum_simplex_duplex_waltz_files
    out:
      [waltz_files]

  fulcrum_duplex_consolidate_bam_metrics:
    run: ../../cwl_tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: fulcrum_duplex_waltz_files
    out:
      [waltz_files]

  marianas_simplex_duplex_consolidate_bam_metrics:
    run: ../../cwl_tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: marianas_simplex_duplex_waltz_files
    out:
      [waltz_files]

  marianas_duplex_consolidate_bam_metrics:
    run: ../../cwl_tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: marianas_duplex_waltz_files
    out:
      [waltz_files]


  ################################################
  # Aggregate Bam Metrics (standard and fulcrum) #
  ################################################

  standard_aggregate_bam_metrics:
    run: ../../cwl_tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: standard_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  fulcrum_simplex_duplex_aggregate_bam_metrics:
    run: ../../cwl_tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: fulcrum_simplex_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  fulcrum_duplex_aggregate_bam_metrics:
    run: ../../cwl_tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: fulcrum_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  marianas_simplex_duplex_aggregate_bam_metrics:
    run: ../../cwl_tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: marianas_simplex_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  marianas_duplex_aggregate_bam_metrics:
    run: ../../cwl_tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: marianas_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]


  #################
  # Innovation-QC #
  #################

  simplex_duplex_innovation_qc:
    run: ../../cwl_tools/innovation-qc/innovation-qc.cwl
    in:
      standard_waltz_metrics: standard_aggregate_bam_metrics/output_dir
      marianas_waltz_metrics: marianas_simplex_duplex_aggregate_bam_metrics/output_dir
      fulcrum_waltz_metrics: fulcrum_simplex_duplex_aggregate_bam_metrics/output_dir
      title_file: title_file
    out:
      [qc_pdf]

  duplex_innovation_qc:
    run: ../../cwl_tools/innovation-qc/innovation-qc.cwl
    in:
      standard_waltz_metrics: standard_aggregate_bam_metrics/output_dir
      marianas_waltz_metrics: marianas_duplex_aggregate_bam_metrics/output_dir
      fulcrum_waltz_metrics: fulcrum_duplex_aggregate_bam_metrics/output_dir
      title_file: title_file
    out:
      [qc_pdf]
