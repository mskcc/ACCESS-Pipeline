cwlVersion: v1.0

class: Workflow

requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_params/schemas/bcftools.yaml

inputs:

  bcftools_params: ../../resources/run_params/schemas/bcftools.yaml#bcftools_params

  vcf_vardict:
    type: File
    secondaryFiles: [.tbi]

  vcf_mutect:
    type: File
    secondaryFiles: [.tbi]

  tumor_sample_name: string
  normal_sample_name: string

outputs:

  combined_vcf:
    type: File
    outputSource: concat/concat_vcf_output_file

steps:

  create_vcf_file_array:
    in:
      vcf_vardict: vcf_vardict
      vcf_mutect: vcf_mutect

    out: [vcf_files]

    run:
      class: ExpressionTool

      requirements:
        - class: InlineJavascriptRequirement

      inputs:
        vcf_vardict:
          type: File
          secondaryFiles:
            - .tbi

        vcf_mutect:
          type: File
          secondaryFiles:
            - .tbi

      outputs:
        vcf_files:
          type: File[]
          secondaryFiles:
            - .tbi

      expression: "${
        var project_object = {};
        project_object['vcf_files'] = [inputs.vcf_vardict, inputs.vcf_mutect];
        return project_object;
      }"

  concat:
    run: ../../cwl_tools/bcftools/bcftools_concat.cwl
    in:
      bcftools_params: bcftools_params
      vcf_files: create_vcf_file_array/vcf_files
      tumor_sample_name: tumor_sample_name
      normal_sample_name: normal_sample_name
      allow_overlaps:
        valueFrom: $(inputs.bcftools_params.allow_overlaps)
      rm_dups:
        valueFrom: $(inputs.bcftools_params.rm_dups)
      output:
        valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.combined-variants.vcf')
    out: [concat_vcf_output_file]