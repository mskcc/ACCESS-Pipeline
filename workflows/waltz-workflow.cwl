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
  doap:name: waltz-workflow
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

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}


inputs:

  input_bam:
    type: File

  coverage_threshold:
    type: string

  # todo - use Files!
  gene_list:
    type: string

  bed_file:
    type: string

  min_mapping_quality:
    type: string

  reference_fasta:
    type: string

  reference_fasta_fai:
    type: string

outputs:
  pileup:
    type: File
    outputSource: pileup_metrics/pileup

  waltz_output_files:
    type:
      type: array
      items: File
    outputSource: grouped_waltz_files/waltz_files

steps:

  count_reads:
    run: ./cmo-waltz.CountReads/0.0.0/cmo-waltz.CountReads.cwl
    in:
      input_bam: input_bam
      coverage_threshold: coverage_threshold
      gene_list: gene_list
      bed_file: bed_file
    out: [
      covered_regions,
      fragment_sizes,
      read_counts
      ]

  pileup_metrics:
    run: ./cmo-waltz.PileupMetrics/0.0.0/cmo-waltz.PileupMetrics.cwl
    in:
      input_bam: input_bam
      min_mapping_quality: min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      bed_file: bed_file
    out: [
      pileup,
      pileup_without_duplicates,
      intervals,
      intervals_without_duplicates
      ]

  grouped_waltz_files:
    run: ./innovation-group-waltz-files/innovation-group-waltz-files.cwl
    in:
      covered_regions: count_reads/covered_regions
      fragment_sizes: count_reads/fragment_sizes
      read_counts: count_reads/read_counts
      pileup: pileup_metrics/pileup
      pileup_without_duplicates: pileup_metrics/pileup_without_duplicates
      intervals: pileup_metrics/intervals
      intervals_without_duplicates: pileup_metrics/intervals_without_duplicates
    out: [waltz_files]

