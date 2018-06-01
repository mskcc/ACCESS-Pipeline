#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [make_umi_qc_tables.sh]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  noise:
    type: File
    inputBinding:
      position: 1

outputs:

  plots:
    type: File[]
    outputBinding:
      glob: $('*.pdf')
