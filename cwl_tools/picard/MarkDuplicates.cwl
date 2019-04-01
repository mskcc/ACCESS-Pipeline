cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx4g
- -jar
- $(inputs.picard)
- MarkDuplicates

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 2
    outdirMax: 100000

doc: |
  None

inputs:
  java: string
  picard: string

  input_bam:
    type: File
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: ['null', string]
    doc: The output file to write marked records to
    default: $( inputs.input_bam.basename.replace('.bam', '_MD.bam') )
    inputBinding:
      prefix: O=
      valueFrom: $( inputs.input_bam.basename.replace('.bam', '_MD.bam') )
      separate: false

  M:
    type: ['null', string]
    doc: File to write duplication metrics to Required.
    default: $( inputs.input_bam.basename.replace('.bam', '.md_metrics') )
    inputBinding:
      prefix: M=
      valueFrom: $( inputs.input_bam.basename.replace('.bam', '.md_metrics') )
      separate: false

  tmp_dir:
    type: ['null', string]
    inputBinding:
      prefix: TMP_DIR=
      separate: false

  validation_stringency:
    type: ['null', string]
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
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

  assume_sorted:
    type: boolean?
    default: true
    inputBinding:
      prefix: ASSUME_SORTED=true

  duplicate_scoring_strategy:
    type: string
    inputBinding:
      prefix: DUPLICATE_SCORING_STRATEGY=
      separate: false

outputs:

  bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.input_bam.basename.replace('.bam', '_MD.bam'))

  # Todo: unnecessary output
  bai:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.basename.replace('.bam', '_MD.bai'))

  mdmetrics:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.basename.replace('.bam', '.md_metrics'))
