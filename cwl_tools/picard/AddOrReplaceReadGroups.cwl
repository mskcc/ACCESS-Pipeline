#!/usr/bin/env cwl-runner

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
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl

inputs:
  java: string
  arrg: string
  sample: ../../resources/schema_defs/Sample.cwl#Sample

  input_bam:
    type: File?
    inputBinding:
      prefix: I=
      separate: false

  O:
    type: string?
    doc: Output file (bam or sam).
    default: $(inputs.input_bam.basename.replace(".sam", "_srt.bam"))
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $(inputs.input_bam.basename.replace(".sam", "_srt.bam"))

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
    type: string
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

  output_sample:
    name: output_sample
    type: ../../resources/schema_defs/Sample.cwl#Sample
    outputBinding:
      glob: '*'
      outputEval: |
        ${
          var output_sample = inputs.sample;

          output_sample.rg_bam_1 = self.filter(function(x) {
            return x.basename === inputs.input_bam.basename.replace(".sam", "_srt.bam")
          })[0];

          output_sample.rg_bai_1 = self.filter(function(x) {
            return x.basename === inputs.input_bam.basename.replace(".sam", "_srt.bai")
          })[0];

          return output_sample
        }
