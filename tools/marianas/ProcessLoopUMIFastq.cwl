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
  doap:name: innovation-umi-trimming
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: cwl-wrapper
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

class: CommandLineTool

baseCommand: [cmo_process_loop_umi_fastq]

arguments: ["-server", "-Xms8g", "-Xmx8g", "-cp"]

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4
    coresMin: 1

doc: Marianas UMI Clipping module

inputs:
  fastq1:
    type:
    - string
    - File
    inputBinding:
      prefix: --fastq1

  fastq2:
    type:
    - string
    - File
    inputBinding:
      prefix: --fastq2

  sample_sheet:
    type: File
    inputBinding:
      prefix: --sample_sheet

  umi_length:
    type: string
    inputBinding:
      prefix: --umi_length

  output_project_folder:
    type: string
    inputBinding:
      prefix: --output_project_folder

outputs:
  processed_fastq_1:
    type: File
    outputBinding:
      glob: ${ return "**/" + inputs.fastq1.split('/').pop() }

  processed_fastq_2:
    type: File
    outputBinding:
      glob: ${ return "**/" + inputs.fastq2.split('/').pop() }

  composite_umi_frequencies:
    type: File
    outputBinding:
      glob: ${ return "**/composite-umi-frequencies.txt" }

  info:
    type: File
    outputBinding:
      glob: ${ return "**/info.txt" }

  output_sample_sheet:
    type: File
    outputBinding:
      glob: ${ return "**/SampleSheet.csv" }

  umi_frequencies:
    type: File
    outputBinding:
      glob: ${ return "**/umi-frequencies.txt" }
