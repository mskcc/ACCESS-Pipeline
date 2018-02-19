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
- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java

arguments:
- -Xmx16g
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

  I:
    type:
    - 'null'
    - File
    - type: array
      items: string
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: ['null', string]
    doc: Output file (bam or sam).
    default: $( inputs.I.basename.replace(".sam", "_RG.bam") )
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $( inputs.I.basename.replace(".sam", "_RG.bam") )

  SO:
    type: ['null', string]
    doc: Optional sort order to output in. If not supplied OUTPUT is in the same order
      as INPUT. Default value - null. Possible values - {unsorted, queryname, coordinate}
    inputBinding:
      prefix: SO=
      separate: false

  LB:
    type: string
    doc: Read Group Library Required.
    inputBinding:
      prefix: RGLB=
      separate: false

  CN:
    type: ['null', string]
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

  DS:
    type: ['null', string]
    doc: Read Group description Default value - null.
    inputBinding:
      prefix: DS=
      separate: false

  SM:
    type: string
    doc: Read Group sample name Required.
    inputBinding:
      prefix: RGSM=
      separate: false

  ID:
    type: ['null', string]
    doc: Read Group ID Default value - 1. This option can be set to 'null' to clear
      the default value.
    inputBinding:
      prefix: RGID=
      separate: false

  PL:
    type: string
    doc: Read Group platform (e.g. illumina, solid) Required.
    inputBinding:
      prefix: PL=
      separate: false

  TMP_DIR:
    type: ['null', string]
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  VERBOSITY:
    type: ['null', string]
    inputBinding:
      prefix: VERBOSITY=
      separate: false

  VALIDATION_STRINGENCY:
    type: ['null', string]
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
      separate: false

  COMPRESSION_LEVEL:
    type: ['null', string]
    inputBinding:
      prefix: COMPRESSION_LEVEL=
      separate: false

  CREATE_INDEX:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: CREATE_INDEX=true

  QUIET:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --QUIET=
      separate: false

  CREATE_MD5_FILE:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --CREATE_MD5_FILE=
      separate: false

  MAX_RECORDS_IN_RAM:
    type: ['null', string]
    inputBinding:
      prefix: MAX_RECORDS_IN_RAM=
      separate: false

  REFERENCE_SEQUENCE:
    type: ['null', string]
    inputBinding:
      prefix: REFERENCE_SEQUENCE=
      separate: false

  stderr:
    type: ['null', string]
    doc: log stderr to file
    inputBinding:
      prefix: --stderr

  stdout:
    type: ['null', string]
    doc: log stdout to file
    inputBinding:
      prefix: --stdout

outputs:

  bam:
    type: File
    outputBinding:
      glob: $( inputs.I.basename.replace(".sam", "_RG.bam") )

  bai:
    type: File?
    outputBinding:
      glob: |-
        ${
          if (inputs.O)
            return inputs.O.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '').replace(/\.sam/,'') + ".bai";
          return null;
        }
