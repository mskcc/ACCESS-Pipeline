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
  doap:name: cmo-picard.MarkDuplicates
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

# /opt/common/CentOS_6/java/jdk1.8.0_31/bin/java
# -Xmx4g
# Todo:
# -jar /home/patelju1/software/picard-2.8.1.jar
# MarkDuplicates
# I=MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt.bam
# O=MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt_MD.bam
# Todo:
# ASSUME_SORTED=true
# Todo:
# METRICS_FILE=MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt_MD.metrics
# TMP_DIR=/ifs/work/scratch/
# COMPRESSION_LEVEL=0
# CREATE_INDEX=true
# VALIDATION_STRINGENCY=LENIENT
# Todo:
# DUPLICATE_SCORING_STRATEGY=SUM_OF_BASE_QUALITIES

baseCommand:
#- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java
- /opt/common/CentOS_6/java/jdk1.8.0_31/bin/java

arguments:
- -Xmx4g
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/MarkDuplicates-1.96.jar

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 2

doc: |
  None

inputs:

  I:
    type: File
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: ['null', string]
    doc: The output file to write marked records to
    default: $( inputs.I.basename.replace(".bam", "_MD.bam") )
    inputBinding:
      prefix: O=
      valueFrom: $( inputs.I.basename.replace(".bam", "_MD.bam") )
      separate: false

  M:
    type: ['null', string]
    doc: File to write duplication metrics to Required.
    default: $( inputs.I.basename.replace(".bam", ".metrics") )
    inputBinding:
      prefix: M=
      valueFrom: $( inputs.I.basename.replace(".bam", ".metrics") )
      separate: false

  TMP_DIR:
    type: ['null', string]
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  VALIDATION_STRINGENCY:
    type: ['null', string]
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
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

# todo: need to updat picard for this?:
#  DUPLICATE_SCORING_STRATEGY:
#    type: string?
#    default: ${ return 'SUM_OF_BASE_QUALITIES' }
#    inputBinding:
#      prefix: DUPLICATE_SCORING_STRATEGY=
#      separate: false
#      valueFrom: ${ return 'SUM_OF_BASE_QUALITIES' }

  ASSUME_SORTED:
    type: boolean?
    default: true
    inputBinding:
      prefix: ASSUME_SORTED=true

outputs:

  bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $( inputs.I.basename.replace(".bam", "_MD.bam") )

  bai:
    type: File?
    outputBinding:
      glob: |
        ${
          if (inputs.O)
            return inputs.O.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '').replace(/\.bam/,'') + ".bai";
          return null;
        }

  mdmetrics:
    type: File
    outputBinding:
      glob: $( inputs.I.basename.replace(".bam", ".metrics") )
