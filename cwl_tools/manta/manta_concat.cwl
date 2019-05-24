cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

arguments:
- head
- -n
- '1'
- $(inputs.sv_calls[0].path)

- shellQuote: false
  valueFrom: '>'

- all_calls.txt

- shellQuote: false
  valueFrom: '&&'

- cat
- $(inputs.sv_calls)

- shellQuote: false
  valueFrom: '|'

- grep
- -vP
- "^TumorId"

# Need this to prevent nonzero exit code if grep runs on header only
- shellQuote: false
  valueFrom: '||'
- 'true'

- shellQuote: false
  valueFrom: '>>'

- all_calls.txt

inputs:

  sv_calls: File[]

outputs:

  concatenated_vcf:
    type: File
    outputBinding:
      glob: all_calls.vcf
