#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
# Todo: Reported bug in 0.7.5a which introduces randomness related to number of threads used:
# https://www.biostars.org/p/90390/
- /opt/common/CentOS_6/bwa/bwa-0.7.5a/bwa

# Todo: cleaner way to provide inputs after arguments
# https://www.biostars.org/p/303637/
# Answer: This can be done with:
#argument:
#  - valueFrom: "./example/example-files"
#    position: 2
#    separate: false
#    prefix: "-Djava.io.tmpdir="
#
#  - valueFrom: "/usr/local/bin/GenomeAnalysisTK.jar"
#    position: 3
#    prefix: "-jar"
#
#  - valueFrom: "HaplotypeCaller"
#    position: 4
#    prefix: "-T"

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

# todo: LB should be lane number?
# Example -R usage from Impact:
#-R '@RG     ID:MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000     LB:0    SM:MSK-L-009-bc-IGO-05500-DY-6  PL:Illumina     PU:bc209        CN:BergerLab_MSKCC'

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 4

inputs:

  fastq1: File
  fastq2: File
  reference_fasta: string
  reference_fasta_fai: string

  sam:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --sam
  t:
    type: ['null', string]
    default: '4'

  ID: string
  LB: int
  SM: string
  PL: string
  PU: string
  CN: string

# Todo: Understand the difference between stdout & > usage in this file
# Compare logs with Impact
stdout: $(inputs.fastq1.basename.replace('_R1', '').replace('.fastq.gz', '_aln.sam'))

outputs:

  output_sam:
    type: File
    outputBinding:
      glob: $(inputs.fastq1.basename.replace('_R1', '').replace('.fastq.gz', '_aln.sam'))
