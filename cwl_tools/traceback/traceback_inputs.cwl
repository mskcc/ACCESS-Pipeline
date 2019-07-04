cwlVersion: cwl:v1.0

class: CommandLineTool

requirements:
- class: StepInputExpressionRequirement: {}
- class: InlineJavascriptRequirement: {}
- class: MultipleInputFeatureRequirement: {}
- class: ResourceRequirement:
  ramMin: 4000
  coresMin: 1

#baseCommand: traceback_inputs
arguments:
- python
- $('/home/jayakumg/software/dev/cwl/cwl-impact/ACCESS-DMP-VC/cwl_tools/traceback/traceback_inputs.py')

doc: |
  Combine all variants from current project with any prior tumor informed mutations, if provided, into a maf.

arguments:


inputs:
  title_file:
    type: File?
    doc: Sample Meta information
    inputBinding:
      prefix: --title_file

  combined_vcf
  

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
