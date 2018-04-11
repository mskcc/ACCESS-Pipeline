#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

inputs:
  input_bam:
    type: File

baseCommand: [samtools]

arguments:
  - view
  - $(inputs.input_bam)
  - '|'
  - awk
  - '{ print $1 "\t" $3 "\t" $4 "\t" $4 + length($10) - 1 }'
  - '>'
  - $( inputs.input_bam.basename.replace(".bam", "_readNames.bed") )

outputs:
  read_names:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_readNames.bed") )
