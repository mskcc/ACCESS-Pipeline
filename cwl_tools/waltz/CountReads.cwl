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
  doap:name: cmo-waltz.CountReads
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cmo-waltz.CountReads
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

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_31/bin/java

arguments:
# todo: why server?
- -server
- -Xms4g
- -Xmx4g
- -cp
- /home/johnsoni/Innovation-Pipeline/vendor_tools/Waltz-2.0.jar
- org.mskcc.juber.waltz.countreads.CountReads

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      position: 1

  coverage_threshold:
    type: int
    inputBinding:
      position: 2

  gene_list:
    type: string
    inputBinding:
      position: 3

  bed_file:
    type: File
    inputBinding:
      position: 4

outputs:

  covered_regions:
    type: File
    outputBinding:
      glob: '*.covered-regions'

  fragment_sizes:
    type: File
    outputBinding:
      glob: '*.fragment-sizes'

  read_counts:
    type: File
    outputBinding:
      glob: '*.read-counts'