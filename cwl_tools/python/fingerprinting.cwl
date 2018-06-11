#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [fingerprinting]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  output_directory:
    type: string
    inputBinding:
      prefix: -o

  waltz_directory_A:
    type: Directory
    inputBinding:
      prefix: -a

  waltz_directory_B:
    type: Directory
    inputBinding:
      prefix: -b

  FP_config_file:
    type: File
    inputBinding:
      prefix: -c

  title_file:
    type: File
    inputBinding:
      prefix: -t

outputs:

  all_fp_results:
    type: Directory
    outputBinding:
      glob: $('./FPResults')

  FPFigures:
    type: File?
    outputBinding:
      glob: $('./FPResults/FPFigures.pdf')
