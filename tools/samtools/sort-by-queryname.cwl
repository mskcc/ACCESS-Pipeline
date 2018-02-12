cwlVersion: v1.0

class: CommandLineTool

requirements:
    - class: ShellCommandRequirement

baseCommand: samtools

arguments:
  - sort
  - -n
  - $(inputs.input_bam)
  - '>'
  - $( inputs.input_bam.basename + ".sorted" )

outputs:

inputs:
  bam:
    type: File
    inputBinding:
      position: 1

outputs:
  bam_sorted_queryname:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename + ".sorted" )
