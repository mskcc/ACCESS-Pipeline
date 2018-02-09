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
  doap:name: cmo-marianas.ProcessUmiBam
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: cmo-marianas.ProcessUmiBam
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

inputs:
  input_bam: File

  reference_fasta: string
#    secondaryFiles: $( inputs.reference_fasta.path + '.fai' )
  reference_fasta_fai: string

  mismatches: string
  wobble: string
  min_consensus_percent: string
  output_dir: string

  pileup: File

  # todo: use
  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_marianasProcessUmiBam.bam") )
    inputBinding:
      prefix: --output_bam_filename
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_marianasProcessUmiBam.bam") )

outputs:
  output_fastq_1:
    type: File
    outputSource: gzip_fastq_1/output

  output_fastq_2:
    type: File
    outputSource: gzip_fastq_2/output

steps:

  first_pass:
    run: ../tools/marianas/SimplexDuplexUMIBamToCollapsedFastqFirstPass.cwl
    in:
      input_bam: input_bam
      pileup: pileup
      mismatches: mismatches
      wobble: wobble
      min_consensus_percent: min_consensus_percent

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      output_dir: output_dir
    out:
      [first_pass_output_file, alt_allele_file]

  sort_by_mate_position:
    # todo - can use an existing sort cwl?
    run: ../tools/marianas-sort/marianas-sort.cwl
    in:
      first_pass_file: first_pass/first_pass_output_file
    out:
      [output_file]

  second_pass:
    run: ../tools/marianas/SimplexDuplexUMIBamToCollapsedFastqSecondPass.cwl
    in:
      input_bam: input_bam

      first_pass_sorted: sort_by_mate_position/output_file

      pileup: pileup
      mismatches: mismatches
      wobble: wobble
      min_consensus_percent: min_consensus_percent

      reference_fasta: reference_fasta
      referene_fasta_fai: reference_fasta_fai

      output_dir: output_dir
    out:
      [collapsed_fastq_1, collapsed_fastq_2]

  gzip_fastq_1:
    run: ../tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: second_pass/collapsed_fastq_1
    out:
      [output]

  gzip_fastq_2:
    run: ../tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: second_pass/collapsed_fastq_2
    out:
      [output]
