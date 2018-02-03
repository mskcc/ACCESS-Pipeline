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
  doap:name: innovation-map-read-names-to-umis
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: innovation-map-read-names-to-umis
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

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4
    coresMin: 1

inputs:
  read_names:
    type: File

baseCommand: [innovation_map_read_names_to_umis]

arguments:
  - $(inputs.read_names)
  - $( inputs.read_names.basename.replace("_readNames.bed", "_Duplex_UMI_for_readNames.fastq") )

outputs:
  annotated_fastq:
    type: File
    outputBinding:
      glob: $( inputs.read_names.basename.replace("_readNames.bed", "_Duplex_UMI_for_readNames.fastq") )
