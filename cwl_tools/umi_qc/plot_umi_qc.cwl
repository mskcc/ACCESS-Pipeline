#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [plot_umi_qc.r]

requirements:
- class: InlineJavascriptRequirement
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs.family_sizes)

inputs:

  family_sizes:
    type: File
    inputBinding:
      position: 1

outputs:

  plots:
    type: File[]
    outputBinding:
      glob: $('*.pdf')
