#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

inputs:
  - id: input_fastq
    type: File
    inputBinding:
      position: 0

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.input_fastq.basename + '.gz')

baseCommand: [gzip, -c]

stdout: $(inputs.input_fastq.basename + '.gz')