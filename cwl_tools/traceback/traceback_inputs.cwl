cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1

baseCommand: [traceback_inputs]

doc: |
  Combine all variants from current project with any prior tumor informed mutations, if provided, into a maf.

inputs:

  title_file:
    type: File
    inputBinding:
      prefix: --title_file

  exonic_filtered_mutations:
    type: File
    inputBinding:
      prefix: --exonic_filtered

  silent_filtered_mutations:
    type: File
    inputBinding:
      prefix: --silent_filtered

  traceback_input_mutations:
    type: File?
    inputBinding:
      prefix: --ti_mutations

outputs:
  traceback_genotype_inputs:
    type: File
    outputBinding:
      glob: traceback_inputs.maf
