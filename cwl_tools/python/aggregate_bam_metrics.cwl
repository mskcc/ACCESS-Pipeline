#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

baseCommand: /home/johnsoni/Innovation-Pipeline/python_tools/innovation_aggregate_bam_metrics.py

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
