cwlVersion: v1.0

class: CommandLineTool

baseCommand: [calculate_noise.sh]

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing: $(inputs.waltz_directory.listing)

inputs:

  waltz_directory: Directory

  output_dir_name: string

  good_positions_A:
    type: File
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

  waltz_folder_with_noise:
    type: Directory
    outputBinding:
      glob: .
      outputEval: |
        ${
          self[0].basename = inputs.output_dir_name;
          return self[0]
        }
