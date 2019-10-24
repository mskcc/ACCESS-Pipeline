cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx30g
- -jar
- $(inputs.gatk)
- -T
- BaseRecalibrator

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 32000
    coresMin: 8
    outdirMax: 100000

doc: |
  None

inputs:
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
