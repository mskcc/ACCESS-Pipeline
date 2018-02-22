cwlVersion: v1.0

class: CommandLineTool

requirements:
    - class: ShellCommandRequirement

baseCommand: samtools

arguments:
  - view

  - $(inputs.h)
  - $(inputs.region)

  - $(inputs.b)

  - $(inputs.F)
  - $(inputs.filter_mask)

  - $(inputs.f)
  - $(inputs.filter_mask_2)

  - $(inputs.input_bam)

  - '>'
  - $( inputs.input_bam.basename + ".sorted" )

inputs:

  bam:
    type: File
    inputBinding:
      position: 1

outputs:

  bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename + ".sorted" )
