cwlVersion: v1.0

class: CommandLineTool

baseCommand: [fingerprinting]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  output_directory:
    type: string
    inputBinding:
      prefix: --output_dir

  waltz_directory_A:
    type: Directory
    inputBinding:
      prefix: --waltz_dir_A

  waltz_directory_B:
    type: Directory
    inputBinding:
      prefix: --waltz_dir_B

  waltz_directory_A_duplex:
    type: Directory
    inputBinding:
      prefix: --waltz_dir_A_duplex

  waltz_directory_B_duplex:
    type: Directory
    inputBinding:
      prefix: --waltz_dir_B_duplex

  FP_config_file:
    type: File
    inputBinding:
      prefix: --fp_config

  title_file:
    type: File
    inputBinding:
      prefix: --title_file

outputs:

  all_fp_results:
    type: Directory
    outputBinding:
      glob: './FPResults'

  FPFigures:
    type: File
    outputBinding:
      glob: './FPResults/FPFigures.pdf'

  gender_table:
    type: File
    outputBinding:
      glob: 'MisMatchedGender.txt'

  gender_plot:
    type: File
    outputBinding:
      glob: 'GenderMisMatch.pdf'
