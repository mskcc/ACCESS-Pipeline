cwlVersion: v1.0

class: ExpressionTool

requirements:
  - class: InlineJavascriptRequirement

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
