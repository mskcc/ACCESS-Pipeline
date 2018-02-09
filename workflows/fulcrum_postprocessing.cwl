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
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  input_bam: File

outputs:

  output_fastq_1:
    type: File
    outputSource: gzip_1/output

  output_fastq_2:
    type: File
    outputSource: gzip_2/output

steps:

  sort_bam_queryname:
    run: ../tools/innovation-sort-bam/innovation-sort-bam.cwl
    in:
      input_bam: input_bam
    out:
      [bam_sorted_queryname]

  samtools_fastq:
    run: ../tools/innovation-samtools-fastq/innovation-samtools-fastq.cwl
    in:
      input_bam: sort_bam_queryname/bam_sorted_queryname
    out:
      [output_read_1, output_read_2]

  gzip_1:
    run: ../tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_1
    out:
      [output]

  gzip_2:
    run: ../tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: samtools_fastq/output_read_2
    out:
      [output]
