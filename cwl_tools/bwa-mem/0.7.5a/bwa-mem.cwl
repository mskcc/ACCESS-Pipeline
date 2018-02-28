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
  doap:name: bwa-mem
  doap:revision: 0.7.5a
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

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/bwa/bwa-0.7.5a/bwa

# todo: use inputs for -t & -PM
# (how to include ">" but put -PM before it?)
# todo: "_R2_001_cl.fastq.gz" is fragile

arguments:
- mem
- -t
- $( inputs.t )
- -PM
- -R
- '@RG	ID:$(inputs.ID) LB:$(inputs.LB)  SM:$(inputs.SM)  PL:$(inputs.PL) PU:$(inputs.PU)  CN:$(inputs.CN)'

- $( inputs.reference_fasta )
- $( inputs.fastq1.path )
- $( inputs.fastq2.path )
- '>'
- $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, inputs.output_suffix + '.sam') )

# todo: Need to include (use from IMPACT LOGS though!):
#- -R "@RG\tID:${sample}\tLB:Garbage\tSM:${sample}\tPL:Illumina\tPU:${barcode}\tCN:InnovationLab"
# or rather this:
#-R '@RG     ID:MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000     LB:0    SM:MSK-L-009-bc-IGO-05500-DY-6  PL:Illumina     PU:bc209        CN:BergerLab_MSKCC'

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 4

doc: |
  run bwa mem

inputs:

  fastq1:
    type: File

  fastq2:
    type: File

  output_suffix:
    type: string

  reference_fasta: string

  reference_fasta_fai:
    type: string

  sam:
    type: ['null', boolean]
    default: false
    doc: Produce Sam instead of the default bam (Boolean)
    inputBinding:
      prefix: --sam

  t:
    type: ['null', string]
    doc: INT number of threads [1]
    default: '4'

  R:
    type: ['null', string]
    doc: STR read group header line such as '@RG\tID -foo\tSM -bar' [null]
    inputBinding:
      prefix: -R

  ID:
    type: string?

  LB:
    type: int?

  SM:
    type: string?

  PL:
    type: string?

  PU:
    type: string?

  CN:
    type: string?


stdout: $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, '') + inputs.output_suffix + '.sam' )

outputs:

  output_sam:
    type: File
    outputBinding:
      glob: $( inputs.fastq1.basename.replace(/_R1_.*.fastq.gz/, '') + inputs.output_suffix + '.sam' )
