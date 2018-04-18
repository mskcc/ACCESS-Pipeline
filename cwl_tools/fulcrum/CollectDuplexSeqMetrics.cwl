#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xms8g
- -Xmx8g
- -jar
- $(inputs.fulcrum)
- --tmp-dir=/scratch
- CollectDuplexSeqMetrics

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 10000
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

  u:
    type: string
    default: 'true'
    inputBinding:
      prefix: -u
      valueFrom: ${ return 'true' }

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "") )
    inputBinding:
      prefix: -o
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "") )

outputs:

  metrics:
    type: File
    outputBinding:
      glob: '*.pdf'
