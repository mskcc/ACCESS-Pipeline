#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl

inputs:
  # Todo: why isn't Sample[] working here?
  samples:
    type:
      type: array
      items:
        type: array
        items: ../../resources/schema_defs/Sample.cwl#Sample

outputs:
  output_samples:
    type:
      type: array
      items: ../../resources/schema_defs/Sample.cwl#Sample

expression: |
  ${
    var samples = [];

    for (var i = 0; i < inputs.samples.length; i++) {
      for (var j = 0; j < inputs.samples[i].length; j++) {
        samples.push(inputs.samples[i][j])
      }
    }

    return {
      'output_samples': samples
    };
  }
