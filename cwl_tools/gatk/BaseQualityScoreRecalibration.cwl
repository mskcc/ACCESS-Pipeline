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
  doap:name: gatk.BaseRecalibrator
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 0.0.0

dct:creator:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johjnson
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
- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java

arguments:
- -Xmx30g
- -Djava.io.tmpdir=/scratch
- -jar
# todo: check 3.3 vs 3.5 for version
- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar
- -T
- BaseRecalibrator

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 32000
    coresMin: 8

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      prefix: -I
    secondaryFiles:
    - ^.bai

  reference_fasta:
    type: string
    inputBinding:
      prefix: -R

  nct:
    type: int
    inputBinding:
      prefix: -nct

  rf:
    type: string
    inputBinding:
      prefix: -rf

  known_sites_1:
    type: ['null', File]
    inputBinding:
      prefix: -knownSites

  known_sites_2:
    type: ['null', File]
    inputBinding:
      prefix: -knownSites

  out:
    type:
    - 'null'
    - string
    doc: The output recalibration table file to create
    inputBinding:
      prefix: --out

outputs:

  recal_matrix:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out;
          return null;
        }
