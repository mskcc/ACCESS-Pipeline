cwlVersion: v1.0

class: CommandLineTool

## Todo: Reported bug in 0.7.5a which introduces randomness related to number of threads used:
## https://www.biostars.org/p/90390/
#- /opt/common/CentOS_6/bwa/bwa-0.7.5a/bwa

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
- $(inputs.bwa)
- mem
- -t
- $(inputs.t)
- -PM
- -R
- '@RG	ID:$(inputs.ID)	LB:$(inputs.LB)	SM:$(inputs.SM)	PL:$(inputs.PL)	PU:$(inputs.PU)	CN:$(inputs.CN)'
- $(inputs.reference_fasta)
- $(inputs.fastq1.path)
- $(inputs.fastq2.path)

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 4
    outdirMax: 20000

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

stdout: $(inputs.fastq1.basename.replace('_R1', '').replace('.fastq.gz', '_aln.sam'))

outputs:

  output_sam:
    type: File
    outputBinding:
      glob: $(inputs.fastq1.basename.replace('_R1', '').replace('.fastq.gz', '_aln.sam'))
