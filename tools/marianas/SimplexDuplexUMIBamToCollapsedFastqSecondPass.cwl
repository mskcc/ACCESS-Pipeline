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
  doap:name: cmo-marianas.DuplexUMIBamToCollapsedFastqSecondPass
  doap:revision: 0.5.0
- class: doap:Version
  doap:name: cmo-marianas.DuplexUMIBamToCollapsedFastqSecondPass
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

baseCommand: ['/opt/common/CentOS_6/java/jdk1.8.0_31/bin/java']

arguments:
- '-server'
- '-Xms8g'
- '-Xmx8g'
- '-cp'
- '/home/johnsoni/Innovation-Pipeline-dev/software/Marianas-standard.jar'
- 'org.mskcc.marianas.umi.duplex.DuplexUMIBamToCollapsedFastqSecondPass'

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 1

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      position: 1
#    secondaryFiles: $( ['first-pass.mate-position-sorted.txt'] )

  # todo:
  first_pass_sorted: File

  pileup:
    type: File
    inputBinding:
      position: 2

  mismatches:
    type: string
    inputBinding:
      position: 3

  wobble:
    type: string
    inputBinding:
      position: 4

  min_consensus_percent:
    type: string
    inputBinding:
      position: 5

  reference_fasta:
    type: string
    inputBinding:
      position: 6
#    secondaryFiles: $( inputs.reference_fasta.path + '.fai' )

  reference_fasta_fai: string

  output_dir:
    type: ['null', string]
    inputBinding:
      position: 7

#  output_bam_filename:
#    type: ['null', string]
#    default: $( inputs.input_bam.basename.replace(".bam", "_marianasProcessUmiBam.bam") )
#    inputBinding:
#      prefix: --output_bam_filename
#      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_marianasProcessUmiBam.bam") )

outputs:

  collapsed_fastq_1:
    type: File
    outputBinding:
      glob: 'collapsed_R1_.fastq'

  collapsed_fastq_2:
    type: File
    outputBinding:
      glob: 'collapsed_R2_.fastq'
