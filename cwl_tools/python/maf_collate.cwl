cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

arguments:
- head
- -n
- '1'
- $(inputs.all_maf[0].path)

- shellQuote: false
  valueFrom: '>'

- collated.maf

- shellQuote: false
  valueFrom: '&&'

- cat
- $(inputs.all_maf)

- shellQuote: false
  valueFrom: '|'

- grep
- -vP
- "^Hugo"

# Need this to prevent nonzero exit code if grep runs on header only
- shellQuote: false
  valueFrom: '||'
- 'true'

- shellQuote: false
  valueFrom: '>>'

- collated.maf

inputs:

  all_maf: File[]

outputs:

  collated_maf:
    type: File
    outputBinding:
      glob: collated.maf
