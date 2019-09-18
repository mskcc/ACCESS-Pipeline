#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1

baseCommand: [aggregate_bam_metrics.sh]

inputs:

  output_dir_name: string

  waltz_input_files:
    type: Directory
    inputBinding:
      position: 1

outputs:

  output_dir:
    type: Directory
    outputBinding:
      glob: .
      outputEval: |
        ${
          self[0].basename = inputs.output_dir_name;
          return self[0]
        }
