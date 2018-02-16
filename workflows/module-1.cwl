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
  doap:name: module-1
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
  InlineJavascriptRequirement: {}

inputs:

  fastq1: File
  fastq2: File

  adapter: string
  adapter2: string

  reference_fasta: string
#    secondaryFiles: $( inputs.reference_fasta.path + '.fai' )
  reference_fasta_fai: string

#  bwa_output: string
  add_rg_LB: string
  add_rg_PL: string

  add_rg_ID: string
  add_rg_PU: string

  add_rg_SM: string
  add_rg_CN: string
  tmp_dir: string
  output_suffix: string

steps:

  trimgalore:
      run: ../cwl-tools/trimgalore/0.2.5.mod/trimgalore.cwl
      in:
        adapter: adapter
        adapter2: adapter2
        fastq1: fastq1
        fastq2: fastq2
      out: [clfastq1, clfastq2, clstats1, clstats2]

  bwa_mem:
    run: ../cwl-tools/bwa-mem/0.7.5a/bwa-mem.cwl
    in:
      fastq1: trimgalore/clfastq1
      fastq2: trimgalore/clfastq2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      output_suffix: output_suffix
    out: [output_sam]

  picard.AddOrReplaceReadGroups:
    run: ../cwl-tools/picard/AddOrReplaceReadGroups/1.96/AddOrReplaceReadGroups.cwl
    in:
      I: bwa_mem/output_sam
      LB: add_rg_LB
      PL: add_rg_PL
      ID: add_rg_ID
      PU: add_rg_PU
      SM: add_rg_SM
      CN: add_rg_CN
      SO:
        default: "coordinate"
      TMP_DIR: tmp_dir
    out: [bam, bai]

  picard.MarkDuplicates:
    run: ../cwl-tools/picard/MarkDuplicates/1.96/MarkDuplicates.cwl
    in:
      I: picard.AddOrReplaceReadGroups/bam
      TMP_DIR: tmp_dir
    out: [bam, bai, mdmetrics]

outputs:

  clstats1:
    type: File
    outputSource: trimgalore/clstats1

  clstats2:
    type: File
    outputSource: trimgalore/clstats2

  bam:
    type: File
    outputSource: picard.MarkDuplicates/bam

  bai:
    type: File
    outputSource: picard.MarkDuplicates/bai

  md_metrics:
    type: File
    outputSource: picard.MarkDuplicates/mdmetrics
