# sort -S 8G -k 6,6n -k 8,8n first-pass.txt > first-pass.mate-position-sorted.txt


#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

inputs:
  input_file:
    type: File

  first_pass_file:
    type: File

baseCommand: [sort]

arguments:
- shellQuote: false
  valueFrom: -S 8G -k 6,6n -k 8,8n $( inputs.input_file.path ) > first-pass.mate-position-sorted.txt

outputs:
  output_file:
    type: File
    outputBinding:
      glob: 'first-pass.mate-position-sorted.txt'
