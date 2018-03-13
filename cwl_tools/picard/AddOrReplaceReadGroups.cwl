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
  doap:name: cmo-picard.AddOrReplaceReadGroups
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
- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java

arguments:
- -Xmx4g
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/AddOrReplaceReadGroups-1.96.jar

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 16000
    coresMin: 2

doc: |
  None

inputs:

  input_bam:
    type: File?
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: string?
    doc: Output file (bam or sam).
    default: $( inputs.input_bam.basename.replace(".sam", "_RG.bam") )
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $( inputs.input_bam.basename.replace(".sam", "_RG.bam") )

  sort_order:
    type: string?
    doc: Optional sort order to output in. If not supplied OUTPUT is in the same order
      as INPUT. Default value - null. Possible values - {unsorted, queryname, coordinate}
    inputBinding:
      prefix: SO=
      separate: false

  ID:
    type: string?
    doc: Read Group ID Default value - 1. This option can be set to 'null' to clear
      the default value.
    inputBinding:
      prefix: RGID=
      separate: false

  LB:
    type: int
    doc: Read Group Library Required.
    inputBinding:
      prefix: RGLB=
      separate: false

  CN:
    type: string?
    doc: Read Group sequencing center name Default value - null.
    inputBinding:
      prefix: RGCN=
      separate: false

  PU:
    type: string
    doc: Read Group platform unit (eg. run barcode) Required.
    inputBinding:
      prefix: RGPU=
      separate: false

  SM:
    type: string
    doc: Read Group sample name Required.
    inputBinding:
      prefix: RGSM=
      separate: false

  PL:
    type: string
    doc: Read Group platform (e.g. illumina, solid) Required.
    inputBinding:
      prefix: RGPL=
      separate: false

  tmp_dir:
    type: string?
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
      glob: $( inputs.input_bam.basename.replace(".sam", "_RG.bam") )

  bai:
    type: File
    outputBinding:
      glob: ${ return '*.bai' }
#      glob: $( inputs.I.basename.replace(".sam", "_RG.bai") )
#      glob: ${ return inputs.O.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '').replace(/\.sam/,'') + ".bai"; }
