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
  doap:name: module-3
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
    foaf:mbox: mailto:johnsonsi@mskcc.org

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}


inputs:
  tmp_dir: string
  input_bam: File

  # SortBam
  sort_order: string

  # GroupReads
  grouping_strategy: string
  min_mapping_quality: string
  tag_family_size_counts_output: string

  # CallDuplexConsensusReads
  call_duplex_min_reads: string

  # FilterConsensusReads
  reference_fasta: string
  filter_min_reads: string
  filter_min_base_quality: string

outputs:

  simplex_duplex_fastq_1:
    type: File
    outputSource: simplex_duplex_fulcrum_postprocessing/output_fastq_1

  simplex_duplex_fastq_2:
    type: File
    outputSource: simplex_duplex_fulcrum_postprocessing/output_fastq_2

  duplex_fastq_1:
    type: File
    outputSource: duplex_fulcrum_postprocessing/output_fastq_1

  duplex_fastq_2:
    type: File
    outputSource: duplex_fulcrum_postprocessing/output_fastq_2

  duplex_seq_metrics:
    type: File
    outputSource: collect_duplex_seq_metrics/metrics

steps:

  innovation_extract_read_names:
    run: ../../cwl-tools/innovation-extract-read-names/innovation-extract-read-names.cwl
    in:
      input_bam: input_bam
    out:
      [read_names]

  innovation_map_read_names_to_umis:
    run: ../../cwl-tools/innovation-map-read-names-to-umis/innovation-map-read-names-to-umis.cwl
    in:
      read_names: innovation_extract_read_names/read_names
    out:
      [annotated_fastq]

  annotate_bam_with_umis:
    run: ../../cwl-tools/fulcrum/AnnotateBamWithUmis.cwl
    in:
      input_bam: input_bam
      annotated_fastq: innovation_map_read_names_to_umis/annotated_fastq
    out:
      [output_bam]

  sort_bam:
    run: ../../cwl-tools/fulcrum/SortBam.cwl
    in:
        input_bam: annotate_bam_with_umis/output_bam
        sort_order: sort_order
    out:
      [output_bam]

  set_mate_information:
    run: ../../cwl-tools/fulcrum/SetMateInformation.cwl
    in:
      input_bam: sort_bam/output_bam
    out:
      [output_bam]

  group_reads_by_umi:
    run: ../../cwl-tools/fulcrum/GroupReadsByUmi.cwl
    in:
      strategy: grouping_strategy
      min_mapping_quality: min_mapping_quality
      tag_family_size_counts_output: tag_family_size_counts_output
      input_bam: set_mate_information/output_bam
    out:
      [output_bam]

  collect_duplex_seq_metrics:
    run: ../../cwl-tools/fulcrum/CollectDuplexSeqMetrics.cwl
    in:
      input_bam: group_reads_by_umi/output_bam
    out:
      [metrics]

  call_duplex_consensus_reads:
    run: ../../cwl-tools/fulcrum/CallDuplexConsensusReads.cwl
    in:
      input_bam: group_reads_by_umi/output_bam
      call_duplex_min_reads: call_duplex_min_reads
    out:
      [output_bam]

  filter_consensus_reads:
    run: ../../cwl-tools/fulcrum/FilterConsensusReads.cwl
    in:
      input_bam: call_duplex_consensus_reads/output_bam
      reference_fasta: reference_fasta
      min_reads: filter_min_reads
      min_base_quality: filter_min_base_quality
    out:
      [output_bam]

  simplex_duplex_fulcrum_postprocessing:
    run: ./fulcrum_postprocessing.cwl
    in:
      input_bam: call_duplex_consensus_reads/output_bam
    out:
      [output_fastq_1, output_fastq_2]

  duplex_fulcrum_postprocessing:
    run: ./fulcrum_postprocessing.cwl
    in:
      input_bam: filter_consensus_reads/output_bam
    out:
      [output_fastq_1, output_fastq_2]
