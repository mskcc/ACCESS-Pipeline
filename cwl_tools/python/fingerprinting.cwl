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

  waltz_directory:
    type: Directory
    inputBinding:
      prefix: -w

  FP_config_file:
    type: File
    inputBinding:
      prefix: -c

  expected_match_file:
    type: File?
    inputBinding:
      prefix: -e

outputs:

  all_fp_results:
    type: Directory
    outputBinding:
      glob: $('./FPResults')

  FPFigures:
    type: File
    outputBinding:
      glob: $('./FPResults/FPFigures.pdf')
