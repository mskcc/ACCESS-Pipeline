cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  # SchemaDefRequirement:
  #   types:
  #     - $import: ../resources/run_params/schemas/vcf2maf.yaml
  #     - $import: ../resources/run_params/schemas/gbcms_params.yaml
  #     - $import: ../resources/run_params/schemas/access_filters.yaml
  #     - $import: ../resources/run_tools/ACCESS_variants_run_tools.yaml

inputs:
  project_name: string
  title_file: File
  custom_enst_file: File
  all_maf:
    type: File[]

outputs:
  collated_maf:
    type: File
    outputSource: maf_collate/collated_maf

  filtered_exonic:
    type: File
    outputSource: maf2tsv/filtered_exonic

  dropped_exonic:
    type: File
    outputSource: maf2tsv/dropped_exonic

  filtered_silent:
    type: File
    outputSource: maf2tsv/filtered_silent

  dropped_silent:
    type: File
    outputSource: maf2tsv/dropped_silent

  filtered_nonpanel:
    type: File
    outputSource: maf2tsv/filtered_nonpanel

  dropped_nonpanel:
    type: File
    outputSource: maf2tsv/dropped_nonpanel

steps:
  maf_collate:
    run: ../cwl_tools/python/maf_collate.cwl
    in:
      all_maf: all_maf
      project_name: project_name
    out: [collated_maf]

  maf2tsv:
    run: ../cwl_tools/python/maf2tsv.cwl
    in:
      title_file: title_file
      collated_maf: maf_collate/collated_maf
      canonical_transcript_reference_file: custom_enst_file
    out: [
      filtered_exonic,
      dropped_exonic,
      filtered_silent,
      dropped_silent,
      filtered_nonpanel,
      dropped_nonpanel]