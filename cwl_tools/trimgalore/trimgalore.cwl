#!/usr/bin/env cwl-runner

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
    type: ['null', string]
    inputBinding:
      prefix: -a

  adapter2:
    type: ['null', string]
    inputBinding:
      prefix: -a2

  # Todo: use inputs instead of defaults
  length:
    type: ['null', string]
    default: '25'
    inputBinding:
      prefix: -length

  paired:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --paired

  gzip:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --gzip

  quality:
    type: ['null', string]
    default: '1'
    inputBinding:
      prefix: -q

  stringency:
    type: ['null', string]
    default: '3'
    inputBinding:
      prefix: --stringency

  suppress_warn:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --suppress_warn

outputs:

  clfastq1:
    type: File
    outputBinding:
      glob: ${return inputs.fastq1.basename.replace('.fastq.gz', '_cl.fastq.gz')}

  clfastq2:
    type: File
    outputBinding:
      glob: ${return inputs.fastq2.basename.replace('.fastq.gz', '_cl.fastq.gz')}

  clstats1:
    type: File
    outputBinding:
      glob: ${return inputs.fastq1.basename.replace('.fastq.gz', '_cl.stats')}

  clstats2:
    type: File
    outputBinding:
      glob: ${return inputs.fastq2.basename.replace('.fastq.gz', '_cl.stats')}
