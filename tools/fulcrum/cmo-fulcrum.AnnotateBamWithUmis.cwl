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
  doap:name: cmo-fulcrum.AnnotateBamWithUMIs
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: cmo-fulcrum.AnnotateBamWithUMIs
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

baseCommand: [cmo_fulcrum_annotate_bam_with_umis]

arguments: ["-server", "-Xms8g", "-Xmx8g", "-jar"]

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    # Requires large amount of ram (loads all read names into a java hashmap)
    ramMin: 30
    coresMin: 1

doc: |
  None

inputs:
  tmp_dir:
    type: string
    inputBinding:
      prefix: --tmp_dir

  input_bam:
    type: File
    inputBinding:
      prefix: --input_bam

  annotated_fastq:
    type: File
    inputBinding:
      prefix: --read_names_file

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_fulcrumAnnotated.bam") )
    inputBinding:
      prefix: --output_bam_filename
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_fulcrumAnnotated.bam") )

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_fulcrumAnnotated.bam") )
