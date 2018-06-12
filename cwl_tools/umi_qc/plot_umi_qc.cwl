#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [plot_umi_qc.r]

requirements:
- class: InlineJavascriptRequirement
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs.family_sizes)
  - entry: $(inputs.family_types_A)
  - entry: $(inputs.family_types_B)

inputs:

  family_sizes:
    type: File
    inputBinding:
      position: 1

  family_types_A:
    type: File
    inputBinding:
      position: 2

  family_types_B:
    type: File
    inputBinding:
      position: 3

outputs:

  plots:
    type: File[]
    outputBinding:
      glob: $('*.pdf')
