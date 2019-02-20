cwlVersion: v1.0

class: CommandLineTool

requirements:
  MultipleInputFeatureRequirement: {}
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1

baseCommand: remove_variants

inputs:

  input_maf:
    type: File
    inputBinding:
      prefix: --input_maf

  output_maf:
    type: string
    inputBinding:
      prefix: --output_maf

outputs:

  consolidated_maf:
    type: File
    outputBinding:
      glob: $(inputs.output_maf)