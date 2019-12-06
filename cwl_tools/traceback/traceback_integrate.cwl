cwlVersion: cwl:v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 20000
  coresMin: 1

baseCommand: [traceback_integrate]

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

  exonic_dropped_mutations:
    type: File
    inputBinding:
      prefix: --exonic_dropped
  
  silent_filtered_mutations:
    type: File
    inputBinding:
      prefix: --silent_filtered

  silent_dropped_mutations:
    type: File
    inputBinding:
      prefix: --silent_dropped

  traceback_input_maf:
    type: File
    inputBinding:
      prefix: --traceback_inputs_maf

  traceback_out_maf:
    type: File
    inputBinding:
      prefix: --traceback_out_maf

outputs:
  traceback_final:
    type: File
    outputBinding:
      glob: traceback.txt

  tb_exonic_filtered_mutations:
    type: File
    outputBinding:
      glob: '*_ExonicFiltered.txt'

  tb_exonic_dropped_mutations:
    type: File
    outputBinding:
      glob: '*_ExonicDropped.txt'

  tb_silent_filtered_mutations:
    type: File
    outputBinding:
      glob: '*_SilentFiltered.txt'

  tb_silent_dropped_mutations:
    type: File
    outputBinding:
      glob: '*_SilentDropped.txt'
