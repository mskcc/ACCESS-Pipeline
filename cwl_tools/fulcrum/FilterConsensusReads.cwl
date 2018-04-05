#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/fgbio-0.5.0.jar
- --tmp-dir=/scratch
- FilterConsensusReads

requirements:
  InlineJavascriptRequirement: {}
  # Need this to allow for -M=1 1 1
  ShellCommandRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 1

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      prefix: -i

  reference_fasta:
    type: string
    inputBinding:
      prefix: -r

  min_reads:
    type: string
    inputBinding:
      prefix: -M
      itemSeparator: '='
      shellQuote: false

  min_base_quality:
    type: int
    inputBinding:
      prefix: -N
      itemSeparator: '='

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_fulcFCR.bam") )
    inputBinding:
      prefix: -o
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_fulcFCR.bam") )

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_fulcFCR.bam") )
