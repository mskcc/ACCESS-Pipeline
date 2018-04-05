#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java

arguments:
- -Xmx24g
- -jar
# todo: consolidate?
- /opt/common/CentOS_6/picard/picard-tools-1.96/FixMateInformation.jar

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 26000
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

  output_filename:
    type: ['null', string]
    default: $(inputs.input_bam.basename.replace(".bam", "_FX.bam"))
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $(inputs.input_bam.basename.replace(".bam", "_FX.bam"))

  sort_order:
    type: ['null', string]
    inputBinding:
      prefix: SO=
      separate: false

  tmp_dir:
    type: ['null', string]
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  compression_level:
    type: ['null', int]
    inputBinding:
      prefix: COMPRESSION_LEVEL=
      separate: false

  create_index:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: CREATE_INDEX=true

  validation_stringency:
    type: ['null', string]
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
      separate: false

outputs:

  bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.input_bam.basename.replace(".bam", "_FX.bam"))

  bai:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.basename.replace(".bam", "_FX.bai"))
