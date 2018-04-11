#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  - class: InlineJavascriptRequirement

inputs:

  waltz_input_files:
    type:
      type: array
      items:
        type: array
        items: File

outputs:

  waltz_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: '*'

expression: '${
  var output_files = [];

  for (var i = 0; i < inputs.waltz_input_files.length; i++) {
    for (var j = 0; j < inputs.waltz_input_files[i].length; j++) {
      output_files.push(inputs.waltz_input_files[i][j]);
    }
  }

  return { "waltz_files": output_files }
}'
