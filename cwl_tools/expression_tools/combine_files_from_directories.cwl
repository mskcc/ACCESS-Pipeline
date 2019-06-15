cwlVersion: v1.0

class: ExpressionTool

doc: |
  This tool will combine all files from each of the input directories, into one directory

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 2000

inputs:

  output_directory_name: string

  directories: Directory[]

outputs:

  combined: Directory

expression: |
  ${
    var output_files = [];

    for (var i = 0; i < inputs.directories.length; i++) {
      for (var j = 0; j < inputs.directories[i].listing.length; j++) {
        output_files.push(inputs.directories[i].listing[j]);
      }
    }

    return {
      'combined': {
        'class': 'Directory',
        'basename': inputs.output_directory_name,
        'listing': output_files
      }
    };
  }
