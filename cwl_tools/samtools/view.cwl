cwlVersion: v1.0

class: CommandLineTool

requirements:
    - class: ShellCommandRequirement

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

arguments:
  - view
  - -b
  - ${ if (inputs.paired_only) { return '-f 1' } }
  - ${ if (inputs.mapped_only) { return '-F 4' } }
  - -h
  - $(inputs.bam)
  - $(inputs.region)
  - '>'
  # Unix does not like colons in filenames
  - $( inputs.bam.basename.replace('.bam', '') + inputs.region.replace(':', '-') + '_mapped_paired.bam' )

inputs:

  bam:
    type: File
    inputBinding:
      position: 1

  region:
    type: string

  mapped_only:
    type: boolean

  paired_only:
    type: boolean

outputs:

  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.bam.basename.replace('.bam', '') + inputs.region.replace(':', '-') + '_mapped_paired.bam' )
