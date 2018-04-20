cwlVersion: v1.0

class: CommandLineTool

requirements:
    - class: ShellCommandRequirement

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

arguments:
  - sort
  - $(inputs.bam)
  - '>'
  - $(inputs.bam.basename + '_sorted')

inputs:

  bam:
    type: File

outputs:

  output_bam:
    type: File
    outputBinding:
      glob: $(inputs.bam.basename + '_sorted')
