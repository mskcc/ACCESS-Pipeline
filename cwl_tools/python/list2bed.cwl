cwlVersion: v1.0

class: CommandLineTool

baseCommand: [list2bed]

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 5000
    coresMin: 1

inputs:

  input_file:
    type: [string, File]
    inputBinding:
      prefix: --input_file

  sort:
    type: ['null', boolean]
    default: true
    doc: Whether to sort bed file output
    inputBinding:
      prefix: --sort

  output_filename:
    type: string
    doc: Name for the output bed file
    inputBinding:
      prefix: --output_file

outputs:

  output_file:
    type: File
    outputBinding:
      glob: ${return inputs.output_filename}
