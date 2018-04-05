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
  doap:name: picard
  doap:revision: 1.96
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
#- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java
- $(inputs.java)

arguments:
- -Xmx4g
- -jar
#- /home/johnsoni/Innovation-Pipeline/vendor_tools/AddOrReplaceReadGroups-1.96.jar
- $(inputs.arrg)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 16000
    coresMin: 2

doc: |
  None

inputs:
  java: string
  arrg: string

  input_bam:
    type: File?
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: string?
    doc: Output file (bam or sam).
    default: $(inputs.input_bam.basename.replace(".sam", "_srt.bam"))
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $(inputs.input_bam.basename.replace(".sam", "_srt.bam"))

  sort_order:
    type: string
    inputBinding:
      prefix: SO=
      separate: false

  ID:
    type: string
    inputBinding:
      prefix: RGID=
      separate: false

  LB:
    type: int
    inputBinding:
      prefix: RGLB=
      separate: false

  CN:
    type: string
    inputBinding:
      prefix: RGCN=
      separate: false

  PU:
    type: string
    inputBinding:
      prefix: RGPU=
      separate: false

  SM:
    type: string
    inputBinding:
      prefix: RGSM=
      separate: false

  PL:
    type: string
    inputBinding:
      prefix: RGPL=
      separate: false

  tmp_dir:
    type: string
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  validation_stringency:
    type: string?
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
      separate: false

  compression_level:
    type: int?
    inputBinding:
      prefix: COMPRESSION_LEVEL=
      separate: false

  create_index:
    type: boolean
    default: true
    inputBinding:
      prefix: CREATE_INDEX=true

outputs:

  bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.input_bam.basename.replace(".sam", "_srt.bam"))

  bai:
    type: File
    outputBinding:
      glob: ${return '*.bai'}
