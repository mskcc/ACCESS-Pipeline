cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx4g
- -jar
- $(inputs.arrg)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 16000
    coresMin: 2
    outdirMax: 90000

doc: |
  None

inputs:
  java: string
  arrg: string

  input_sam:
    type: File
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: string
    doc: Output file (bam or sam).
    default: $(inputs.input_sam.basename.replace('.sam', '_srt.bam'))
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $(inputs.input_sam.basename.replace('.sam', '_srt.bam'))

  sort_order:
    type: string
    inputBinding:
      prefix: SO=
      separate: false

  ID:
    type: string
    inputBinding:
      prefix: RGID=
      separate: false

  LB:
    type: int
    inputBinding:
      prefix: RGLB=
      separate: false

  CN:
    type: string
    inputBinding:
      prefix: RGCN=
      separate: false

  PU:
    type: string
    inputBinding:
      prefix: RGPU=
      separate: false

  SM:
    type: string
    inputBinding:
      prefix: RGSM=
      separate: false

  PL:
    type: string
    inputBinding:
      prefix: RGPL=
      separate: false

  tmp_dir:
    type: string?
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  validation_stringency:
    type: string?
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
      separate: false

  compression_level:
    type: int?
    inputBinding:
      prefix: COMPRESSION_LEVEL=
      separate: false

  create_index:
    type: boolean
    default: true
    inputBinding:
      prefix: CREATE_INDEX=true

outputs:

  bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.input_sam.basename.replace('.sam', '_srt.bam'))

  bai:
    type: File
    outputBinding:
      glob: ${return '*.bai'}
