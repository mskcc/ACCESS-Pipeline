#!/usr/bin/env cwl-runner

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
  doap:name: list2bed
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 0.0.0

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

cwlVersion: cwl:v1.0

class: CommandLineTool

baseCommand: /home/johnsoni/Innovation-Pipeline/python_tools/list2bed.py

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 20000
    coresMin: 1

inputs:

  input_file:
    type:
    - string
    - File
    - type: array
      items: string
    inputBinding:
      prefix: --input_file

  sort:
    type: ['null', boolean]
    default: true
    doc: sort bed file output
    inputBinding:
      prefix: --sort

  output_filename:
    type: string
    doc: output bed file
    inputBinding:
      prefix: --output_file

outputs:

  output_file:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.output_filename)
            return inputs.output_filename;
          return null;
        }
