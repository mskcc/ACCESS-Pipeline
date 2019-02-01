cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 2000

inputs:

  bams:
    type:
      type: array
      items:
        type: array
        items: File
    secondaryFiles: ['^.bai']

outputs:

  output_bams:
    type:
      type: array
      items: File
    secondaryFiles: ['^.bai']

expression: |
  ${
    var samples = [];

    for (var i = 0; i < inputs.bams.length; i++) {
      for (var j = 0; j < inputs.bams[i].length; j++) {
        samples.push(inputs.bams[i][j])
      }
    }

    return { "output_bams": samples };
  }
