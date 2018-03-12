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
    foaf:mbox: mailto:johnsonsi@mskcc.org

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  input_bam: File

  tmp_dir: string
  reference_fasta: string
  reference_fasta_fai: string
  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string
  output_suffix: string

outputs:

  bam:
    type: File
    outputSource: post_collapsing_realignment/bam

steps:

  sort_bam_queryname:
    run: ../../cwl_tools/innovation-sort-bam/innovation-sort-bam.cwl
    in:
      input_bam: input_bam
    out:
      [bam_sorted_queryname]

  samtools_fastq:
    run: ../../cwl_tools/innovation-samtools-fastq/innovation-samtools-fastq.cwl
    in:
      input_bam: sort_bam_queryname/bam_sorted_queryname
    out:
      [output_read_1, output_read_2]

  gzip_1:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_1
    out:
      [output]

  gzip_2:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_2
    out:
      [output]

  post_collapsing_realignment:
    run: ../../workflows/module-1.abbrev.cwl
    in:
      tmp_dir: tmp_dir
      fastq1: gzip_1/output
      fastq2: gzip_2/output
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix: output_suffix
    out:
      [bam]
