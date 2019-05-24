cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

arguments:
- head
- -n
- '1'
- $(inputs.vcfs[0].path)

- shellQuote: false
  valueFrom: '>'

- all_calls.txt

- shellQuote: false
  valueFrom: '&&'

- cat
- $(inputs.vcfs)

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

  vcfs: File[]

outputs:

  concatenated_vcf:
    type: File
    outputBinding:
      glob: all_calls.vcf
