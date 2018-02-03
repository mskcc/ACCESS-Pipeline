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
  doap:name: cmo-fulcrum.GroupReadsByUmi
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: cmo-fulcrum.GroupReadsByUmi
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

cwlVersion: "v1.0"

class: CommandLineTool

baseCommand: [cmo_fulcrum_group_reads_by_umi]

arguments: ["-server", "-jar"]

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 50
    coresMin: 1

doc: |
  None

inputs:
  tmp_dir:
    type: string
    inputBinding:
      prefix: --tmp_dir

  strategy:
    type: string
    inputBinding:
      prefix: --strategy

  min_mapping_quality:
    type: string
    inputBinding:
      prefix: --min_mapping_quality

  tag_family_size_counts_output:
    type: string
    inputBinding:
      prefix: --tag_family_size_counts_output

  input_bam:
    type: File
    inputBinding:
      prefix: --input_bam

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_fulcrumGrouped.bam") )
    inputBinding:
      prefix: --output_bam_filename
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_fulcrumGrouped.bam") )

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_fulcrumGrouped.bam") )
