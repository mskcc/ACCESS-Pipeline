#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [plot_noise]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  noise:
    type: File
    inputBinding:
      prefix: --noise_file

  noise_by_substitution:
    type: File
    inputBinding:
      prefix: --noise_by_substitution

outputs:

  noise_alt_percent:
    type: File
    outputBinding:
      glob: $('NoiseAltPercent.pdf')

  noise_contributing_sites:
    type: File
    outputBinding:
      glob: $('NoiseContributingSites.pdf')
