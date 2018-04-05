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
#- /opt/common/CentOS_6/bwa/bwa-0.7.5a/bwa
- $(inputs.bwa)

# Todo: Find a cleaner way to provide inputs after arguments
# https://www.biostars.org/p/303637/
arguments:
- mem
- -t
- $(inputs.t)
- -PM
- -R
- '@RG	ID:$(inputs.ID)	LB:$(inputs.LB)	SM:$(inputs.SM)	PL:$(inputs.PL)	PU:$(inputs.PU)	CN:$(inputs.CN)'
- $(inputs.reference_fasta)
- $(inputs.fastq1.path)
- $(inputs.fastq2.path)
- '>'
- $(inputs.fastq1.basename.replace('_R1', '').replace('.fastq.gz', '_aln.sam'))

# Example -R usage from Impact Pipeline:
#-R '@RG     ID:MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000     LB:0    SM:MSK-L-009-bc-IGO-05500-DY-6  PL:Illumina     PU:bc209        CN:BergerLab_MSKCC'
# Todo: LB == lane number?

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 4

inputs:
  bwa: string

  fastq1: File
  fastq2: File
  reference_fasta: string
  reference_fasta_fai: string
  t:
    type: ['null', string]
    default: '4'
  sam:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --sam

  ID: string
  LB: int
  SM: string
  PL: string
  PU: string
  CN: string

# Todo: Understand the difference between stdout & > usage in this file
stdout: $(inputs.fastq1.basename.replace('_R1', '').replace('.fastq.gz', '_aln.sam'))

outputs:

  output_sam:
    type: File
    outputBinding:
      glob: $(inputs.fastq1.basename.replace('_R1', '').replace('.fastq.gz', '_aln.sam'))
