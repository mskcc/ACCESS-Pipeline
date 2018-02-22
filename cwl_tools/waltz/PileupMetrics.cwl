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
  doap:name: cmo-waltz.PileupMetrics
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cmo-waltz.PileupMetrics
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
- org.mskcc.juber.waltz.Waltz
- PileupMetrics

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
      position: 2
    secondaryFiles: [^.bai]

  min_mapping_quality:
    type: string
    inputBinding:
      position: 1

  reference_fasta:
    type: string
    inputBinding:
      position: 3
    secondaryFiles: $( inputs.reference_fasta.path + '.fai' )

#  reference_fasta_fai:
#    type: string
#    inputBinding:
#      prefix: --reference_fasta_fai

  bed_file:
    type: File
    inputBinding:
      position: 4

# Example Waltz PileupMetrics output files:
#
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-pileup.txt
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-pileup-without-duplicates.txt
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-intervals.txt
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-intervals-without-duplicates.txt

outputs:

  pileup:
    type: File
    outputBinding:
      glob: '*-pileup.txt'

  pileup_without_duplicates:
    type: File
    outputBinding:
      glob: '*-pileup-without-duplicates.txt'

  intervals:
    type: File
    outputBinding:
      glob: '*-intervals.txt'

  intervals_without_duplicates:
    type: File
    outputBinding:
      glob: '*-intervals-without-duplicates.txt'
