#!/usr/bin/env cwl-runner

cwlVersion: cwl:v1.0

class: CommandLineTool

baseCommand: [reverse_clip]

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 5000
    coresMin: 1

inputs:

  fastq_1:
    type: File
    inputBinding:
      position: 1

  fastq_2:
    type: File
    inputBinding:
      position: 2

outputs:

  # Todo: Don't rely on same file suffix being typed into two different files
  reversed_fastq_1:
    type: File
    outputBinding:
      glob: $( inputs.fastq_1.basename.replace(".fastq", "_clipping-reversed.fastq") )

  reversed_fastq_2:
    type: File
    outputBinding:
      glob: $( inputs.fastq_1.basename.replace(".fastq", "_clipping-reversed.fastq") )
