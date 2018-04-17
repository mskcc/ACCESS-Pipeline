#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -jar
- $(inputs.fulcrum)
- --tmp-dir=/scratch
- CallDuplexConsensusReads

requirements:
  InlineJavascriptRequirement: {}
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

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_fulcCDCR.bam") )
    inputBinding:
      prefix: -o
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_fulcCDCR.bam") )

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_fulcCDCR.bam") )
