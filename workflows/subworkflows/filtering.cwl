cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/params/basic-filtering-vardict.yaml
      - $import: ../../resources/schemas/params/basic-filtering-mutect.yaml

inputs:

  basicfiltering_vardict_params: ../../resources/schemas/params/basic-filtering-vardict.yaml#basicfiltering_vardict_params
  basicfiltering_mutect_params: ../../resources/schemas/params/basic-filtering-mutect.yaml#basicfiltering_mutect_params

  mutect_vcf: File
  mutect_callstats: File
  vardict_vcf: File
  tumor_sample_name: string
  normal_sample_name: string

  ref_fasta: File

outputs:

  vardict_norm_vcf:
    type: File
    outputSource: vardict_filtering_step/vcf
    secondaryFiles: [.tbi]

  mutect_norm_vcf:
    type: File
    outputSource: mutect_filtering_step/vcf
    secondaryFiles: [.tbi]

steps:

  mutect_filtering_step:
    run: ../../cwl_tools/basicfiltering/basic-filtering_mutect.cwl
    in:
      basicfiltering_mutect_params: basicfiltering_mutect_params
      total_depth:
        valueFrom: $(inputs.basicfiltering_mutect_params.total_depth)
      allele_depth:
        valueFrom: $(inputs.basicfiltering_mutect_params.allele_depth)
      tumor_normal_ratio:
        valueFrom: $(inputs.basicfiltering_mutect_params.tumor_normal_ratio)
      variant_fraction:
        valueFrom: $(inputs.basicfiltering_mutect_params.variant_fraction)

      inputVcf: mutect_vcf
      inputTxt: mutect_callstats
      tsampleName: tumor_sample_name
      refFasta: ref_fasta
    out: [vcf]

  vardict_filtering_step:
    run: ../../cwl_tools/basicfiltering/basic-filtering_vardict.cwl
    in:
      basicfiltering_vardict_params: basicfiltering_vardict_params
      total_depth:
        valueFrom: $(inputs.basicfiltering_vardict_params.total_depth)
      allele_depth:
        valueFrom: $(inputs.basicfiltering_vardict_params.allele_depth)
      tumor_normal_ratio:
        valueFrom: $(inputs.basicfiltering_vardict_params.tumor_normal_ratio)
      variant_fraction:
        valueFrom: $(inputs.basicfiltering_vardict_params.variant_fraction)
      filter_germline:
        valueFrom: $(inputs.basicfiltering_vardict_params.filter_germline)
      min_qual:
        valueFrom: $(inputs.basicfiltering_vardict_params.min_qual)

      inputVcf: vardict_vcf
      tsampleName: tumor_sample_name
      refFasta: ref_fasta
    out: [vcf]
