cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: ShellCommandRequirement

baseCommand: [mv]

inputs:

  input_file:
    type: File
    inputBinding:
      position: 1

  new_name:
    type: string
    inputBinding:
      position: 2

outputs:

  renamed_file:
    type: File
    outputBinding:
      glob: $(inputs.new_name)
