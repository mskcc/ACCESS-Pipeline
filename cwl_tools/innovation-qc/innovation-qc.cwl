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
  doap:name: innovation-qc
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

cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

baseCommand: innovation_qc_with_groups.py

inputs:
  standard_waltz_metrics:
    type: Directory
    inputBinding:
      prefix: -sw

  marianas_waltz_metrics:
    type: Directory?
    inputBinding:
      prefix: -mw

  fulcrum_waltz_metrics:
    type: Directory?
    inputBinding:
      prefix: -fw

  title_file:
    type: File
    inputBinding:
      prefix: -t

outputs:
  qc_pdf:
    type: File[]
    outputBinding:
      # todo: find pdfs explicitly
      glob: ${ return '**/**/**/*.pdf' }