#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx30g
- -Djava.io.tmpdir=$(inputs.tmp_dir)
- -jar
- $(inputs.gatk)
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
  tmp_dir: string
  java: string
  gatk: string

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
