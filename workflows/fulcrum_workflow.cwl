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

  # AnnotateFastqWithUmis

  # SortBam
  sort_order: string

  # SetMateInformation

  # GroupReads
  grouping_strategy: string
  min_mapping_quality: string
  tag_family_size_counts_output: string

  # CallDuplexConsensusReads

  # FilterConsensusReads
  reference_fasta: File
  filter_min_reads: string
  filter_min_base_quality: string

  # sort_bam_queryname

  # samtools fastq

outputs:
  output_fastq_1:
    type: File
    outputSource: gzip_1/output

  output_fastq_2:
    type: File
    outputSource: gzip_2/output

steps:
  innovation_extract_read_names:
    run: ./innovation-extract-read-names/0.0.0/innovation-extract-read-names.cwl
    in:
      input_bam: input_bam
    out:
      [read_names]

  innovation_map_read_names_to_umis:
    run: ./innovation-map-read-names-to-umis/0.0.0/innovation-map-read-names-to-umis.cwl
    in:
      read_names: innovation_extract_read_names/read_names
    out:
      [annotated_fastq]

  annotate_bam_with_umis:
    run: ./cmo-fulcrum.AnnotateBamWithUmis/0.2.0/cmo-fulcrum.AnnotateBamWithUmis.cwl
    in:
      tmp_dir: tmp_dir
      input_bam: input_bam
      annotated_fastq: innovation_map_read_names_to_umis/annotated_fastq
    out:
      [output_bam]

  sort_bam:
    run: ./cmo-fulcrum.SortBam/0.2.0/cmo-fulcrum.SortBam.cwl
    in:
        tmp_dir: tmp_dir
        input_bam: annotate_bam_with_umis/output_bam
        sort_order: sort_order
    out:
      [output_bam]

  set_mate_information:
    run: ./cmo-fulcrum.SetMateInformation/0.2.0/cmo-fulcrum.SetMateInformation.cwl
    in:
      tmp_dir: tmp_dir
      input_bam: sort_bam/output_bam
    out:
      [output_bam]

  group_reads_by_umi:
    run: ./cmo-fulcrum.GroupReadsByUmi/0.2.0/cmo-fulcrum.GroupReadsByUmi.cwl
    in:
      tmp_dir: tmp_dir
      strategy: grouping_strategy
      min_mapping_quality: min_mapping_quality
      tag_family_size_counts_output: tag_family_size_counts_output
      input_bam: set_mate_information/output_bam
    out:
      [output_bam]

  call_duplex_consensus_reads:
    run: ./cmo-fulcrum.CallDuplexConsensusReads/0.2.0/cmo-fulcrum.CallDuplexConsensusReads.cwl
    in:
      tmp_dir: tmp_dir
      input_bam: group_reads_by_umi/output_bam
    out:
      [output_bam]

  filter_consensus_reads:
    run: ./cmo-fulcrum.FilterConsensusReads/0.2.0/cmo-fulcrum.FilterConsensusReads.cwl
    in:
      tmp_dir: tmp_dir
      input_bam: call_duplex_consensus_reads/output_bam
      reference_fasta: reference_fasta
      min_reads: filter_min_reads
      min_base_quality: filter_min_base_quality
    out:
      [output_bam]

  sort_bam_queryname:
    run: ./innovation-sort-bam/0.0.0/innovation-sort-bam.cwl
    in:
      input_bam: filter_consensus_reads/output_bam
    out:
      [bam_sorted_queryname]

  samtools_fastq:
    run: ./innovation-samtools-fastq/0.0.0/innovation-samtools-fastq.cwl
    in:
      input_bam: sort_bam_queryname/bam_sorted_queryname
    out:
      [output_read_1, output_read_2]

  gzip_1:
    run: ./innovation-gzip-fastq/0.0.0/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_1
    out:
      [output]

  gzip_2:
    run: ./innovation-gzip-fastq/0.0.0/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_2
    out:
      [output]
