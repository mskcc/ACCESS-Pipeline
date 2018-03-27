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
  doap:name: samtools
  doap:revision: 1.3.1
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
    foaf:mbox: mailto:johnsonsi@mskcc.org

cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs['input'])
    entryname: indexed.bam

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

arguments:
- index
- indexed.bam

inputs:
  input:
    type: File

outputs:

  bam_with_bai:
    type: File
    outputBinding:
      glob: indexed.bam
    secondaryFiles:
    - .bai
