#!/usr/bin/env cwl-runner
#
# Note: this file is not used in current pipeline

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx20g
- -Djava.io.tmpdir=/scratch
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar
- -T
- IndelRealigner

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 20000
    coresMin: 8

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      prefix: -I
    secondaryFiles:
    - ^.bai

  reference_fasta:
    type: string
    inputBinding:
      prefix: -R

  # Todo: Use our bedfile instead?
  target_intervals:
    type: File
    inputBinding:
      prefix: -targetIntervals

  # Todo: use correct default syntax
  baq:
    type: ['null', string]
    default: 'RECALCULATE'
    inputBinding:
      prefix: -baq
      valueFrom: 'RECALCULATE'

  known:
    type: File
    inputBinding:
      prefix: -known

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_gatkIR.bam") )
    inputBinding:
      prefix: -o
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_gatkIR.bam") )

outputs:

  bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_gatkIR.bam") )
