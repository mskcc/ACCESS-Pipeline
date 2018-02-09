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
  doap:name: cmo-bwa-mem
  doap:revision: 0.7.5a
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

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/bwa/bwa-0.7.5a/bwa


# todo: specify -t -PM from inputs (how to include ">" but put -PM before it?)

# todo: "_R2_001_cl.fastq.gz" is fragile

#arguments:
#- valueFrom: /usr/local/bin/picard.jar
#  position: 2
#  prefix: -jar

arguments:
- mem
- -PM
- -t
- $( inputs.t )
- $( inputs.reference_fasta )
- $( inputs.fastq1.path )
- $( inputs.fastq2.path )
- '>'
- $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, inputs.output_suffix + '.sam') )

# todo: Need to include:
#- -R "@RG\tID:${sample}\tLB:Garbage\tSM:${sample}\tPL:Illumina\tPU:${barcode}\tCN:InnovationLab"

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 4

doc: |
  run bwa mem

inputs:

  fastq1:
    type:
    - string
    - File

  fastq2:
    type:
    - string
    - File

  output_suffix:
    type: string

#  output:
#    type: ['null', string]
#    default: $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, '') + inputs.output_suffix + '.bam' )
#    inputBinding:
#      prefix: --output
#      valueFrom: $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, '') + inputs.output_suffix + '.bam' )

  reference_fasta: string
#    secondaryFiles: $( inputs.reference_fasta.path + '.fai' )

  reference_fasta_fai:
    type: string

  sam:
    type: ['null', boolean]
    default: false
    doc: Produce Sam instead of the default bam (Boolean)
    inputBinding:
      prefix: --sam

  E:
    type: ['null', string]
    doc: INT gap extension penalty; a gap of size k cost {-O} + {-E}*k [1]
    inputBinding:
      prefix: -E

  d:
    type: ['null', string]
    doc: INT off-diagonal X-dropoff [100]
    inputBinding:
      prefix: -d

  A:
    type: ['null', string]
    doc: INT score for a sequence match [1]
    inputBinding:
      prefix: -A

  C:
    type: ['null', boolean]
    default: false
    doc: append FASTA/FASTQ comment to SAM output
    inputBinding:
      prefix: -C

  c:
    type: ['null', string]
    doc: INT skip seeds with more than INT occurrences [10000]
    inputBinding:
      prefix: -c

  B:
    type: ['null', string]
    doc: INT penalty for a mismatch [4]
    inputBinding:
      prefix: -B

  M:
    type: ['null', boolean]
    default: true
    doc: mark shorter split hits as secondary (for Picard/GATK compatibility)
#    inputBinding:
#      prefix: -M

  L:
    type: ['null', string]
    doc: INT penalty for clipping [5]
    inputBinding:
      prefix: -L

  O:
    type: ['null', string]
    doc: INT gap open penalty [6]
    inputBinding:
      prefix: -O

  R:
    type: ['null', string]
    doc: STR read group header line such as '@RG\tID -foo\tSM -bar' [null]
    inputBinding:
      prefix: -R

  k:
    type: ['null', string]
    doc: INT minimum seed length [19]
    inputBinding:
      prefix: -k

  U:
    type: ['null', string]
    doc: INT penalty for an unpaired read pair [17]
    inputBinding:
      prefix: -U

  t:
    type: ['null', string]
    doc: INT number of threads [1]
    default: '5'

  w:
    type: ['null', string]
    doc: INT band width for banded alignment [100]
    inputBinding:
      prefix: -w

  v:
    type: ['null', string]
    doc: INT verbose level - 1=error, 2=warning, 3=message, 4+=debugging [3]
    inputBinding:
      prefix: -v

  T:
    type: ['null', string]
    doc: INT minimum score to output [30]
    inputBinding:
      prefix: -T

  P:
    type: ['null', boolean]
    default: false
    doc: skip pairing; mate rescue performed unless -S also in use
#    inputBinding:
#      prefix: -P

  S:
    type: ['null', boolean]
    default: false
    doc: skip mate rescue
    inputBinding:
      prefix: -S

  r:
    type: ['null', string]
    doc: FLOAT look for internal seeds inside a seed longer than {-k} * FLOAT [1.5]
    inputBinding:
      prefix: -r

  a:
    type: ['null', boolean]
    default: false
    doc: output all alignments for SE or unpaired PE
    inputBinding:
      prefix: -a

  p:
    type: ['null', string]
    doc: first query file consists of interleaved paired-end sequences
    inputBinding:
      prefix: -p


#outputs:
#
#  output_sam:
#    type: File
#    outputBinding:
#      glob: $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, '') + inputs.output_suffix + '.sam' )


stdout: $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, '') + inputs.output_suffix + '.sam' )

outputs:

  output_sam:
    type: File
    outputBinding:
      glob: $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, '') + inputs.output_suffix + '.sam' )
