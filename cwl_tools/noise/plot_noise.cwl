cwlVersion: v1.0

class: CommandLineTool

baseCommand: [plot_noise]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  title_file:
    type: File
    inputBinding:
      prefix: --title_file

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

  noise_by_substitution:
    type: File
    outputBinding:
      glob: $('noise_by_substitution.pdf')
