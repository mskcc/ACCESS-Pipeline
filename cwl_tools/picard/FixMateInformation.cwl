cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx24g
- -jar
- $(inputs.fix_mate_information)
- TMP_DIR=$(runtime.tmpdir)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 5
    outdirMax: 20000

doc: |
  None

inputs:
  java: string
  fix_mate_information: string

  input_bam:
    type:
    - 'null'
    - File
    inputBinding:
      prefix: I=
      separate: false

  output_filename:
    type: ['null', string]
    default: $(inputs.input_bam.basename.replace('.bam', '_FX.bam'))
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $(inputs.input_bam.basename.replace('.bam', '_FX.bam'))

  sort_order:
    type: ['null', string]
    inputBinding:
      prefix: SO=
      separate: false

  tmp_dir:
    type: string?
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  compression_level:
    type: ['null', int]
    inputBinding:
      prefix: COMPRESSION_LEVEL=
      separate: false

  create_index:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: CREATE_INDEX=true

  validation_stringency:
    type: ['null', string]
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
      separate: false

outputs:

  bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.input_bam.basename.replace('.bam', '_FX.bam'))

  bai:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.basename.replace('.bam', '_FX.bai'))
