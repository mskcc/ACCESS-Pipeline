cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ShellCommandRequirement

baseCommand: [samtools, sort]

arguments:
- $(inputs.input)

- shellQuote: false
  valueFrom: $('>')

- $(inputs.output_name)

inputs:

  input:
    type: File
    doc: Input bam file.

  output_name:
    type: string
    doc: Desired output filename.

outputs:

  sorted_bam:
    type: File
    outputBinding:
      glob: $(inputs.output_name)
