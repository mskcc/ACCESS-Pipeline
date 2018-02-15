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

  fastq1: File[]
  fastq2: File[]
  sample_sheet: File[]

  # ProcessUMIFastq
  umi_length: string
  output_project_folder: string
  outdir: string

  # Trimgalore
  adapter: string[]
  adapter2: string

  # BWA
  genome: string

  # Arrg
  add_rg_PL: string
  add_rg_CN: string
  add_rg_LB: string[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]

  # FX
  fix_mate_information__sort_order: string
  fix_mate_information__validation_stringency: string
  fix_mate_information__compression_level: string
  fix_mate_information__create_index: string

  # Fulcrum
  tmp_dir: string
  reference_fasta: string
  reference_fasta_fai: string

  sort_order: string
  grouping_strategy: string
  min_mapping_quality: string
  tag_family_size_counts_output: string
  call_duplex_min_reads: string
  filter_min_reads: string
  filter_min_base_quality: string

  # Marianas
  marianas__mismatches: string
  marianas__wobble: string
  marianas__min_consensus_percent: string
  marianas_collapsing__outdir: string

  # Waltz
  coverage_threshold: string
  gene_list: string
  bed_file: string
  waltz__min_mapping_quality: string


outputs:

  standard_bams:
    type:
      type: array
      items: File
    outputSource: scatter_step/standard_bams

  standard_waltz_files:
    type: Directory
    outputSource: standard_aggregate_bam_metrics/output_dir

  ###########
  # Fulcrum #
  ###########

  fulcrum_simplex_duplex_bams:
    type:
      type: array
      items: File
    outputSource: scatter_step/fulcrum_simplex_duplex_bams

  fulcrum_simplex_duplex_waltz_files:
    type: Directory
    outputSource: fulcrum_simplex_duplex_aggregate_bam_metrics/output_dir

  fulcrum_duplex_bams:
    type:
      type: array
      items: File
    outputSource: scatter_step/fulcrum_duplex_bams

  fulcrum_duplex_waltz_files:
    type: Directory
    outputSource: fulcrum_duplex_aggregate_bam_metrics/output_dir

  duplex_seq_metrics:
    type:
      type: array
      items: File
    outputSource: scatter_step/duplex_seq_metrics

  ############
  # Marianas #
  ############

  marianas_simplex_duplex_bams:
    type:
      type: array
      items: File
    outputSource: scatter_step/marianas_simplex_duplex_bams

  marianas_simplex_duplex_waltz_files:
    type: Directory
    outputSource: marianas_simplex_duplex_aggregate_bam_metrics/output_dir

  marianas_duplex_bams:
    type:
      type: array
      items: File
    outputSource: scatter_step/marianas_duplex_bams

  marianas_duplex_waltz_files:
    type: Directory
    outputSource: marianas_duplex_aggregate_bam_metrics/output_dir

  ##############
  # QC reports #
  ##############

#  standard_aggregated_waltz_output:
#    type: Directory
#    outputSource: standard_aggregate_bam_metrics/output_dir
#
#  fulcrum_aggregated_waltz_output:
#    type: Directory
#    outputSource: fulcrum_aggregate_bam_metrics/output_dir

  simplex_duplex_qc_report:
    type: File
    outputSource: simplex_duplex_innovation_qc/qc_pdf

  duplex_qc_report:
    type: File
    outputSource: duplex_innovation_qc/qc_pdf

steps:

  scatter_step:
    run: ./innovation_pipeline.scatter.cwl

    in:
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

      # Fulcrum
      tmp_dir: tmp_dir
      sort_order: sort_order
      grouping_strategy: grouping_strategy
      min_mapping_quality: min_mapping_quality
      tag_family_size_counts_output: tag_family_size_counts_output
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      # CallDuplexConsensusReads
      call_duplex_min_reads: call_duplex_min_reads
      # FilterConsensusReads
      filter_min_reads: filter_min_reads
      filter_min_base_quality: filter_min_base_quality

      # Marianas
      marianas__mismatches: marianas__mismatches
      marianas__wobble: marianas__wobble
      marianas__min_consensus_percent: marianas__min_consensus_percent
      marianas_collapsing__outdir: marianas_collapsing__outdir

      # Waltz
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
      waltz__min_mapping_quality: waltz__min_mapping_quality

    # I7 adapter is different for each sample, I5 is not
    scatter: [adapter, fastq1, fastq2, sample_sheet, add_rg_LB, add_rg_ID, add_rg_PU, add_rg_SM]

    scatterMethod: dotproduct

    out: [
      output_sample_sheet,

      standard_bams,

      fulcrum_simplex_duplex_bams,
      fulcrum_duplex_bams,
      duplex_seq_metrics,

      marianas_simplex_duplex_bams,
      marianas_duplex_bams,

      standard_waltz_files,
      fulcrum_simplex_duplex_waltz_files,
      fulcrum_duplex_waltz_files,
      marianas_simplex_duplex_waltz_files,
      marianas_duplex_waltz_files
    ]


  standard_consolidate_bam_metrics:
    run: ../tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: scatter_step/standard_waltz_files
    out:
      [waltz_files]

  fulcrum_simplex_duplex_consolidate_bam_metrics:
    run: ../tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: scatter_step/fulcrum_simplex_duplex_waltz_files
    out:
      [waltz_files]

  fulcrum_duplex_consolidate_bam_metrics:
    run: ../tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: scatter_step/fulcrum_duplex_waltz_files
    out:
      [waltz_files]

  marianas_simplex_duplex_consolidate_bam_metrics:
    run: ../tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: scatter_step/marianas_simplex_duplex_waltz_files
    out:
      [waltz_files]

  marianas_duplex_consolidate_bam_metrics:
    run: ../tools/innovation-consolidate-bam-metrics/innovation-consolidate-bam-metrics.cwl
    in:
      waltz_input_files: scatter_step/marianas_duplex_waltz_files
    out:
      [waltz_files]


  ################################################
  # Aggregate Bam Metrics (standard and fulcrum) #
  ################################################

  standard_aggregate_bam_metrics:
    run: ../tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: standard_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  fulcrum_simplex_duplex_aggregate_bam_metrics:
    run: ../tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: fulcrum_simplex_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  fulcrum_duplex_aggregate_bam_metrics:
    run: ../tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: fulcrum_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  marianas_simplex_duplex_aggregate_bam_metrics:
    run: ../tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: marianas_simplex_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]

  marianas_duplex_aggregate_bam_metrics:
    run: ../tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl
    in:
      waltz_input_files: marianas_duplex_consolidate_bam_metrics/waltz_files
    out:
      [output_dir]


  #################
  # Innovation-QC #
  #################

  simplex_duplex_innovation_qc:
    run: ../tools/innovation-qc/innovation-qc.cwl
    in:
      standard_waltz_metrics: standard_aggregate_bam_metrics/output_dir
      marianas_waltz_metrics: marianas_simplex_duplex_aggregate_bam_metrics/output_dir
      fulcrum_waltz_metrics: fulcrum_simplex_duplex_aggregate_bam_metrics/output_dir
      title_file: title_file
    out:
      [qc_pdf]

  duplex_innovation_qc:
    run: ../tools/innovation-qc/innovation-qc.cwl
    in:
      standard_waltz_metrics: standard_aggregate_bam_metrics/output_dir
      marianas_waltz_metrics: marianas_duplex_aggregate_bam_metrics/output_dir
      fulcrum_waltz_metrics: fulcrum_duplex_aggregate_bam_metrics/output_dir
      title_file: title_file
    out:
      [qc_pdf]
