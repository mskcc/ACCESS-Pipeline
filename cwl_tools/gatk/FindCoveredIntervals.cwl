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
  doap:name: gatk.FindCoveredIntervals
  doap:revision: 3.3-0
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

# todo: is this the version we use in Impact for this step? if so then use it
#baseCommand: /ifs/work/zeng/dmp/resources/GenomeAnalysisTK-2.6-5-gba531bd/GenomeAnalysisTK.jar
# /opt/common/CentOS_6/gatk/GenomeAnalysisTK-3.3-0/GenomeAnalysisTK.jar
baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
- -Xmx20g
- -Djava.io.tmpdir=/scratch
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar
- -T
- FindCoveredIntervals

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 15000
    coresMin: 1

doc: |
  None

inputs:

  input_file:
    type: File
    inputBinding:
      prefix: --input_file
    doc: Input file containing sequence data (SAM or BAM)

#  intervals:
#    type:
#    - 'null'
#    - type: array
#      items: string
#      inputBinding:
#        prefix: --intervals
#    doc: One or more genomic intervals over which to operate
#    inputBinding:
# todo: How does this function if there was no prefix included?
#      prefix:

  reference_sequence:
    type: string
    inputBinding:
      prefix: --reference_sequence

  out:
    type: string
    doc: An output file created by the walker. Will overwrite contents if file exists.
    inputBinding:
      prefix: --out

outputs:

  fci_list:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out;
          return null;
        }
