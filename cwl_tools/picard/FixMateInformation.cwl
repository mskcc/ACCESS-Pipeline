#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx24g
- -jar
- $(inputs.fix_mate_information)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 26000
    coresMin: 5
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl

doc: |
  None

inputs:
  java: string
  fix_mate_information: string
  sample: ../../resources/schema_defs/Sample.cwl#Sample

  input_bam:
    type:
    - 'null'
    - File
    inputBinding:
      prefix: I=
      separate: false

  output_filename:
    type: ['null', string]
    default: $(inputs.input_bam.basename.replace(".bam", "_FX.bam"))
    inputBinding:
      prefix: O=
      separate: false
      valueFrom: $(inputs.input_bam.basename.replace(".bam", "_FX.bam"))

  sort_order:
    type: ['null', string]
    inputBinding:
      prefix: SO=
      separate: false

  tmp_dir:
    type: ['null', string]
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

  output_sample:
    name: output_sample
    type: ../../resources/schema_defs/Sample.cwl#Sample
    outputBinding:
      glob: '*'
      outputEval: |
        ${
          var output_sample = inputs.sample;

          output_sample.fx_bam_1 = self.filter(function(x) {
            return x.basename === inputs.input_bam.basename.replace('.bam', '_FX.bam')
          })[0];

          output_sample.fx_bai_1 = self.filter(function(x) {
            return x.basename === inputs.input_bam.basename.replace('.bam', '_FX.bai')
          })[0];

          return output_sample
        }
