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
  doap:name: fulcrum
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

class: CommandLineTool

baseCommand:
#- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java
- $(inputs.java)

arguments:
- -jar
#- /home/johnsoni/Innovation-Pipeline/vendor_tools/fgbio-0.5.0.jar
- $(inputs.fulcrum)
- --tmp-dir=/scratch
- FilterConsensusReads

requirements:
  InlineJavascriptRequirement: {}
  # Need this to allow for -M=1 1 1
  ShellCommandRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 1

doc: |
  None

inputs:
  java: string
  fulcrum: string

  input_bam:
    type: File
    inputBinding:
      prefix: -i

  reference_fasta:
    type: string
    inputBinding:
      prefix: -r

  min_reads:
    type: string
    inputBinding:
      prefix: -M
      itemSeparator: '='
      shellQuote: false

  min_base_quality:
    type: int
    inputBinding:
      prefix: -N
      itemSeparator: '='

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_fulcFCR.bam") )
    inputBinding:
      prefix: -o
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_fulcFCR.bam") )

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_fulcFCR.bam") )
