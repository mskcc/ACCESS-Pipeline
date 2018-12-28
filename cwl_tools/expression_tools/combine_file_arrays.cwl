cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    # Note: 1024 is the lowest value possible here because Toil will use `floor(ramMin / 1024)`
    ramMin: 2000

inputs:
  files_list_one: File[]
  files_list_two: File[]

outputs:
  combined_files: File[]

expression: |
  ${
    var combined_files = inputs.files_list_one.concat(inputs.files_list_two);
    return {'combined_files': combined_files }
  }
