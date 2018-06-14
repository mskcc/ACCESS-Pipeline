#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [gender_check]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  output_dir:
    type: string
    inputBinding:
      prefix: -o

  waltz_dir:
    type: Directory
    inputBinding:
      prefix: -w

  title_file:
    type: File
    inputBinding:
      prefix: -t

outputs:

  gender_table:
    type: File?
    outputBinding:
      glob: $('MisMatchedGender.txt')

  gender_plot:
    type: File?
    outputBinding:
      glob: $('GenderMisMatch.pdf')
