#!/usr/bin/env cwl-runner
#
# Note: this file is not used in current pipeline

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
  doap:name: gatk.IndelRealignment
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 0.0.0

dct:creator:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johjnson
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
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
- -Xmx20g
- -Djava.io.tmpdir=/scratch
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar
- -T
- IndelRealigner

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 20000
    coresMin: 8

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      prefix: -I
    secondaryFiles:
    - ^.bai

  reference_fasta:
    type: File
    inputBinding:
      prefix: -R

  # Todo: Use our bedfile instead?
  target_intervals:
    type: File
    inputBinding:
      prefix: -targetIntervals

  # Todo: use correct default syntax
  baq:
    type: ['null', string]
    default: 'RECALCULATE'
    inputBinding:
      prefix: -baq
      valueFrom: 'RECALCULATE'

  known:
    type: File
    inputBinding:
      prefix: -known

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_gatkIR.bam") )
    inputBinding:
      prefix: -o
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_gatkIR.bam") )

outputs:

  bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_gatkIR.bam") )
