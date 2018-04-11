#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

arguments:
- shellQuote: false
# todo: need this on separate lines
  valueFrom: fastq -1 $( inputs.input_bam.basename.replace(".bam", "_R1.fastq") ) -2 $( inputs.input_bam.basename.replace(".bam", "_R2.fastq") ) $(inputs.input_bam.path)

inputs:

  input_bam:
    type: File

outputs:

  output_read_1:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_R1.fastq") )

  output_read_2:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_R2.fastq") )
