#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs.input)
    entryname: $(inputs.input.basename)

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

arguments:
- index

inputs:

  input:
    type: File
    inputBinding:
      position: 1

outputs:

  bam_with_bai:
    type: File
    outputBinding:
      glob: $(inputs.input.basename)
    secondaryFiles:
    - .bai
