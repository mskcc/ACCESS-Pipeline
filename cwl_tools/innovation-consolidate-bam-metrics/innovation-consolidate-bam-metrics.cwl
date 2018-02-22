#!/usr/bin/env/cwl-runner

$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/
  doap: http://usefulinc.com/ns/doap#

$schemas:
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf
- http://usefulinc.com/ns/doap#

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
