#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -jar
- $(inputs.fulcrum)
- --tmp-dir=/scratch
- SortBam

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    # Requires large amount of memory
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
      prefix: --input
      itemSeparator: '='

  sort_order:
    type: string
    inputBinding:
      prefix: --sort-order
      itemSeparator: '='

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_fulcSB.bam") )
    inputBinding:
      prefix: --output
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_fulcSB.bam") )

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_fulcSB.bam") )
