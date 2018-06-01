#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [plot_noise.r]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  noise:
    type: File
    inputBinding:
      position: 1

  noise_by_substitution:
    type: File
    inputBinding:
      position: 2

outputs:

  plots:
    type: File[]
    outputBinding:
      glob: $('*.pdf')
