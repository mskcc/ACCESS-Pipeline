cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

successCodes: [0, 1]

arguments:
- head
- -n
- '1'
- $(inputs.all_maf[0].path)

- shellQuote: false
  valueFrom: '>'

- $(inputs.project_name + '_collated.maf')

- shellQuote: false
  valueFrom: '&&'

# Need to use subshell in order to gather stdout from second command to append to file
- shellQuote: false
  valueFrom: '('

- cat
- $(inputs.all_maf)

- shellQuote: false
  valueFrom: '|'

- grep
- -vP
- "^Hugo"

# Need to use subshell in order to gather stdout from second command to append to file
- shellQuote: false
  valueFrom: ')'

- shellQuote: false
  valueFrom: '>>'

- $(inputs.project_name + '_collated.maf')

inputs:

  all_maf:
    type: File[]
  project_name:
    type: string

outputs:

  collated_maf:
    type: File
    outputBinding:
      glob: $(inputs.project_name + '_collated.maf')
