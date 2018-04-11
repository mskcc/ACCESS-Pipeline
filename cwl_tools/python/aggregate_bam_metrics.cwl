#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

baseCommand: [aggregate_bam_metrics]

inputs:
  waltz_input_files:
    type:
      type: array
      items: File
    inputBinding:
      position: 1

outputs:
  output_dir:
    type: Directory
    outputBinding:
      glob: .
