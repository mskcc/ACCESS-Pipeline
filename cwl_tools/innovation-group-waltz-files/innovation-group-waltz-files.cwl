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
  doap:name: innovation-group-waltz-files
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: innovation-group-waltz-files
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

  covered_regions:
    type: File

  fragment_sizes:
    type: File

  read_counts:
    type: File

  pileup:
    type: File

  pileup_without_duplicates:
    type: File

  intervals:
    type: File

  intervals_without_duplicates:
    type: File

outputs:
  waltz_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: '*'

expression: '${
  var output_files = [];

  output_files.push(inputs.covered_regions);
  output_files.push(inputs.fragment_sizes);
  output_files.push(inputs.read_counts);
  output_files.push(inputs.pileup);
  output_files.push(inputs.pileup_without_duplicates);
  output_files.push(inputs.intervals);
  output_files.push(inputs.intervals_without_duplicates);

  return { "waltz_files": output_files }
}'
