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

# /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java
# -Xmx4g
# -jar /opt/common/CentOS_6/picard/picard-tools-1.96//AddOrReplaceReadGroups.jar
# I=MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln.sam
# O=MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt.bam
# SO=coordinate
# RGID=MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000
# RGLB=0
# RGPL=Illumina
# RGPU=bc209
# RGSM=MSK-L-009-bc-IGO-05500-DY-6
# RGCN=MSKCC
# TMP_DIR=/ifs/work/scratch/
# COMPRESSION_LEVEL=0
# CREATE_INDEX=true
# VALIDATION_STRINGENCY=LENIENT

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

  I:
    type: File?
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: string?
    doc: Output file (bam or sam).
    default: $( inputs.I.basename.replace(".sam", "_RG.bam") )
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $( inputs.I.basename.replace(".sam", "_RG.bam") )

  SO:
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

  TMP_DIR:
    type: string?
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  VALIDATION_STRINGENCY:
    type: string?
    default: ${ return 'LENIENT' }
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
      valueFrom: ${ return 'LENIENT' }
      separate: false

  COMPRESSION_LEVEL:
    type: string?
    inputBinding:
      prefix: COMPRESSION_LEVEL=
      separate: false

  CREATE_INDEX:
    type: boolean
    default: true
    inputBinding:
      prefix: CREATE_INDEX=true

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
