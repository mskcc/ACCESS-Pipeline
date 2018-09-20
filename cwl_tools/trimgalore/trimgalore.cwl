cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.perl)
- $(inputs.trimgalore)

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 16000
  coresMin: 2
  outdirMax: 20000

doc: |
  None

inputs:
  perl: string
  trimgalore: string

  fastq1:
    type: File
    inputBinding:
      position: 999

  fastq2:
    type: File
    inputBinding:
      position: 1000

  adapter:
    type: string?
    inputBinding:
      prefix: -a

  adapter2:
    type: string?
    inputBinding:
      prefix: -a2

  length:
    type: int
    inputBinding:
      prefix: -length

  paired:
    type: boolean
    inputBinding:
      prefix: --paired

  gzip:
    type: boolean
    inputBinding:
      prefix: --gzip

  quality:
    type: int
    inputBinding:
      prefix: -q

  stringency:
    type: int
    inputBinding:
      prefix: --stringency

  suppress_warn:
    type: boolean
    inputBinding:
      prefix: --suppress_warn

outputs:

  clfastq1:
    type: File
    outputBinding:
      glob: $(inputs.fastq1.basename.replace('.fastq.gz', '_cl.fastq.gz'))

  clfastq2:
    type: File
    outputBinding:
      glob: $(inputs.fastq2.basename.replace('.fastq.gz', '_cl.fastq.gz'))

  clstats1:
    type: File
    outputBinding:
      glob: $(inputs.fastq1.basename.replace('.fastq.gz', '_cl.stats'))

  clstats2:
    type: File
    outputBinding:
      glob: $(inputs.fastq2.basename.replace('.fastq.gz', '_cl.stats'))
