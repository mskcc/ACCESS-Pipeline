#!/usr/bin/env/cwl-runner

$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/
  doap: http://usefulinc.com/ns/doap#

$schemas:
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf
- http://usefulinc.com/ns/doap#

doap:release:
- class: doap:Version
  doap:name: innovation-merge-directories
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: innovation-merge-directories
  doap:revision: 1.0.0

dct:creator:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsoni@mskcc.org

dct:contributor:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsoni@mskcc.org

cwlVersion: v1.0

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement

inputs:
  files_1:
    type:
      type: array
      items:
        type: array
        items: File
    inputBinding:
      position: 1

  files_2:
    type:
      type: array
      items:
        type: array
        items: File
    inputBinding:
      position: 2

outputs:
  output_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: '*'

expression: '${
  var flattened_files_1 = [].concat.apply([], inputs.files_1);
  var flattened_files_2 = [].concat.apply([], inputs.files_2);

  return { "output_files": flattened_files_1.concat(flattened_files_2) }
}'
