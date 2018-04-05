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
  doap:name: module-2.5
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

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:

  title_file: File
  bam: File

  reference_fasta: string
  reference_fasta_fai: string

  # Arrg
  add_rg_PL: string
  add_rg_CN: string
  add_rg_LB: int
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string

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

  standard_pileup: File

outputs:

  # Fulcrum
  fulcrum_simplex_duplex_singleton_bams:
    type: File
    outputSource: fulcrum/simplex_duplex_singleton

  fulcrum_simplex_duplex_bams:
    type: File
    outputSource: fulcrum/simplex_duplex

  fulcrum_duplex_bams:
    type: File
    outputSource: fulcrum/duplex

  duplex_seq_metrics:
    type: File
    outputSource: fulcrum/duplex_seq_metrics

  # Marianas
  marianas_simplex_duplex_bams:
    type: File
    outputSource: module_1_post_marianas_simplex_duplex/bam

  marianas_duplex_bams:
    type: File
    outputSource: module_1_post_marianas_duplex/bam

steps:

  ###########################
  # Collapsing with Fulcrum #
  ###########################

  fulcrum:
    run: ./fulcrum/fulcrum_workflow.cwl
    in:
      tmp_dir: tmp_dir
      input_bam: bam
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      sort_order: fulcrum__sort_order
      grouping_strategy: fulcrum__grouping_strategy
      min_mapping_quality: fulcrum__min_mapping_quality
      tag_family_size_counts_output: fulcrum__tag_family_size_counts_output
      call_duplex_min_reads: fulcrum__call_duplex_min_reads
      filter_min_base_quality: fulcrum__filter_min_base_quality
      filter_min_reads__simplex_duplex: fulcrum__filter_min_reads__simplex_duplex
      filter_min_reads__duplex: fulcrum__filter_min_reads__duplex

      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
    out:
      [simplex_duplex_singleton, simplex_duplex, duplex, duplex_seq_metrics]

  ############################
  # Collapsing with Marianas #
  ############################

  marianas_simplex_duplex:
    run: ./marianas/marianas_collapsing_workflow_simplex_duplex.cwl
    in:
      input_bam: bam
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      pileup: standard_pileup
      mismatches: marianas__mismatches
      wobble: marianas__wobble
      min_consensus_percent: marianas__min_consensus_percent
      output_dir: marianas_collapsing__outdir
    out:
     [output_fastq_1, output_fastq_2]

  module_1_post_marianas_simplex_duplex:
    run: ./module-1_abbrev.cwl
    in:
      tmp_dir: tmp_dir
      fastq1: marianas_simplex_duplex/output_fastq_1
      fastq2: marianas_simplex_duplex/output_fastq_2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix:
        valueFrom: ${ return '_marianasSimplexDuplex' }
    out:
      [bam, bai]

  marianas_duplex:
    run: ./marianas/marianas_collapsing_workflow_duplex.cwl
    in:
      input_bam: bam
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      pileup: standard_pileup
      mismatches: marianas__mismatches
      wobble: marianas__wobble
      min_consensus_percent: marianas__min_consensus_percent
      output_dir: marianas_collapsing__outdir
    out:
     [output_fastq_1, output_fastq_2]

  module_1_post_marianas_duplex:
    run: ./module-1_abbrev.cwl
    in:
      tmp_dir: tmp_dir
      fastq1: marianas_duplex/output_fastq_1
      fastq2: marianas_duplex/output_fastq_2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix:
        valueFrom: ${ return '_marianasDuplex' }
    out:
      [bam, bai]
