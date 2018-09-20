cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

baseCommand: [gzip, -c]

stdout: $(inputs.input_fastq.basename + '.gz')

inputs:
  input_fastq:
    type: File
    inputBinding:
      position: 0

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.input_fastq.basename + '.gz')
