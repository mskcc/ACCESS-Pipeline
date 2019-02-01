#!toil-cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 2000

inputs:

  output_directory_name: string

  files:
    type:
      type: array
      items:
        type: array
        items: File

outputs:

  directory:
    type: Directory

# This tool returns a Directory object,
# which holds all output files from the list
# of supplied input files
expression: |
  ${
    var output_files = [];

    for (var i = 0; i < inputs.files.length; i++) {
      for (var j = 0; j < inputs.files[i].length; j++) {
        output_files.push(inputs.files[i][j]);
      }
    }

    return {
      'directory': {
        'class': 'Directory',
        'basename': inputs.output_directory_name,
        'listing': output_files
      }
    };
  }
