cwlVersion: v1.0

class: CommandLineTool

requirements:
  MultipleInputFeatureRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

baseCommand: tag_hotspots

inputs:

  input_maf:
    type: File
    inputBinding:
      prefix: --input_maf

  input_hotspot:
    type: File
    inputBinding:
      prefix: --input_hotspot

  output_maf:
    type: string
    inputBinding:
      prefix: --output_maf

outputs:

  hotspot_tagged_maf:
    type: File
    outputBinding:
      glob: $(inputs.output_maf)