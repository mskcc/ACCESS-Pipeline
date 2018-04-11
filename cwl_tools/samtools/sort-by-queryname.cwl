#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: ShellCommandRequirement

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

# Todo: Combine with sort-by-coordinate
# How to optionally include "-n" before the ">"?
arguments:
  - sort
  - -n
  - $(inputs.input_bam)
  - '>'
  - $(inputs.input_bam.basename.replace(".bam", "_samtSRT.bam"))

inputs:
  input_bam:
    type: File

outputs:
  bam_sorted_queryname:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.basename.replace(".bam", "_samtSRT.bam"))
