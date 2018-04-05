#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs['input'])
    entryname: indexed.bam

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

arguments:
- index
- indexed.bam

inputs:
  input:
    type: File

outputs:

  bam_with_bai:
    type: File
    outputBinding:
      glob: indexed.bam
    secondaryFiles:
    - .bai
