cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

inputs:
  first_pass_file:
    type: File

baseCommand: [sort]

arguments:
- shellQuote: false
  valueFrom: -S 8G -k 6,6n -k 8,8n $(inputs.first_pass_file.path) > first-pass.mate-position-sorted.txt

outputs:
  output_file:
    type: File
    outputBinding:
      glob: 'first-pass.mate-position-sorted.txt'
