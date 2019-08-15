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
- $(inputs.sv_calls[0].path)

- shellQuote: false
  valueFrom: '>'

- $(inputs.project_name + "_AllAnnotatedSVs.txt")

- shellQuote: false
  valueFrom: '&&'

# Need to use subshell in order to gather stdout from second command to append to file
- shellQuote: false
  valueFrom: '('

- cat
- $(inputs.sv_calls)

- shellQuote: false
  valueFrom: '|'

- grep
- -vP
- "^TumorId"

# Need to use subshell in order to gather stdout from second command to append to file
- shellQuote: false
  valueFrom: ')'

- shellQuote: false
  valueFrom: '>>'

- $(inputs.project_name + "_AllAnnotatedSVs.txt")

inputs:
  project_name:
    type: string
  sv_calls: 
    type: File[]

outputs:

  concatenated_vcf:
    type: File
    outputBinding:
      glob: $(inputs.project_name + "_AllAnnotatedSVs.txt")
