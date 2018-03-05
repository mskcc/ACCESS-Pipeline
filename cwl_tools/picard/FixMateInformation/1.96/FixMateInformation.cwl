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
  doap:name: cmo-picard.FixMateInformation
  doap:revision: 2.17.10
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
- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java

arguments:
- -Xmx24g
- -jar
- /opt/common/CentOS_6/picard/picard-tools-1.96/FixMateInformation.jar
# todo: what's the difference between FixMateInformation.jar and picard-1.96.jar?
# - /home/johnsoni/Innovation-Pipeline/vendor_tools/picard_2.17.10.jar
# DMP version (access denied):
# - /ifs/work/zeng/dmp/resources/picard-tools-1.96/FixMateInformation.jar

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 20000
    coresMin: 5

doc: |
  None

inputs:

  input_bam:
    type:
    - 'null'
    - File
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: ['null', string]
    doc: The output file to write to. If no output file is supplied, the input file
      is overwritten. Default value - null.
    default: $( inputs.input_bam.basename.replace(".bam", "_FX.bam") )
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_FX.bam") )

  SO:
    type: ['null', string]
    doc: Optional sort order if the OUTPUT file should be sorted differently than
      the INPUT file. Possible values - {unsorted, queryname, coordinate}
    inputBinding:
      prefix: SO=
      separate: false

  TMP_DIR:
    type: ['null', string]
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  COMPRESSION_LEVEL:
    type: ['null', int]
    inputBinding:
      prefix: COMPRESSION_LEVEL=
      separate: false

  CREATE_INDEX:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: CREATE_INDEX=true

  VALIDATION_STRINGENCY:
    type: ['null', string]
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
      separate: false

outputs:

  bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_FX.bam") )

  bai:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_FX.bai") )
