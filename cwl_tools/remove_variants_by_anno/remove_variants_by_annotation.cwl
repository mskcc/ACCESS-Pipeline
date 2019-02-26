cwlVersion: v1.0

class: CommandLineTool

requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
  MultipleInputFeatureRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

baseCommand: remove_variants_by_annotation

inputs:

  input_maf:
    type: File
    inputBinding:
      prefix: --input_maf

  input_interval:
    type: File
    inputBinding:
      prefix: --input_interval

  kept_output_maf:
    type: string
    inputBinding:
      prefix: --kept_output_maf
  
  dropped_output_maf:
    type: string
    inputBinding:
      prefix: --dropped_output_maf

  dropped_NGR_output_maf:
    type: string
    inputBinding:
      prefix: --dropped_NGR_output_maf

outputs:

  kept_rmvbyanno_maf:
    type: File
    outputBinding:
      glob: $(inputs.kept_output_maf)

  dropped_rmvbyanno_maf:
    type: File
    outputBinding:
      glob: $(inputs.dropped_output_maf)

  dropped_NGR_rmvbyanno_maf:
    type: File
    outputBinding:
      glob: $(inputs.dropped_NGR_output_maf)
