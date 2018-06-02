#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [calculate-noise.sh]

requirements:
  - class: InlineJavascriptRequirement
#  - class: InitialWorkDirRequirement
#    listing:
#      - $(inputs.waltz_directory)

inputs:

  waltz_directory:
    type: Directory
    inputBinding:
      position: 1

outputs:

  noise:
    type: File
    outputBinding:
      glob: $('noise.txt')

  noise_by_substitution:
    type: File
    outputBinding:
      glob: $('noise-by-substitution.txt')

#  waltz_dir_with_noise:
#    type: Directory
#    outputBinding:
#      glob: '*'
