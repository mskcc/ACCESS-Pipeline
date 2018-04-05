#!/usr/bin/env cwl-runner

cwlVersion: cwl:v1.0

class: CommandLineTool

baseCommand: /home/johnsoni/Innovation-Pipeline/python_tools/list2bed.py

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 5000
    coresMin: 1

inputs:

  input_file:
    type:
    - string
    - File
    - type: array
      items: string
    inputBinding:
      prefix: --input_file

  sort:
    type: ['null', boolean]
    default: true
    doc: sort bed file output
    inputBinding:
      prefix: --sort

  output_filename:
    type: string
    doc: output bed file
    inputBinding:
      prefix: --output_file

outputs:

  output_file:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.output_filename)
            return inputs.output_filename;
          return null;
        }
