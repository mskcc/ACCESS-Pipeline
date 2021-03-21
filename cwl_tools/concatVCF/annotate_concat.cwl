cwlVersion: v1.0

class: CommandLineTool

baseCommand: annotate_concat

requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
  MultipleInputFeatureRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

doc: |
  Annotates common variants in concatenated vcf and another vcf with tag from inputted header file

inputs:

  combined_vcf:
    type: [string, File]
    doc: Combined Input vcf that gets annotated
    inputBinding:
      prefix: --combined_vcf

  anno_with_vcf:
    type: [string, File]
    doc: Input vcf to annoted with
    inputBinding:
      prefix: --anno_with_vcf

  anno_header:
    type: [string, File]
    doc: Input txt header file
    inputBinding:
      prefix: --anno_header

outputs:

  annotated_concat_vcf_output_file:
    type: File
    outputBinding:
      glob: ${return inputs.combined_vcf.basename.replace('.vcf', '_anno.vcf')}
