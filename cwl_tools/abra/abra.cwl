#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx60g
- -Djava.io.tmpdir=$(inputs.tmp_dir)
- -jar
- $(inputs.abra)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 62000
    coresMin: 8
    outdirMax: 60000

# Todo: It would be nice to have this
# but unfortunately PATH is not a defined
# variable in the CWL parsing environment.
# For now we rely on including BWA at the beginning
# of our PATH before starting the run
#
#  EnvVarRequirement:
#    envDef:
#      PATH: $(inputs.bwa + ':' + PATH)

inputs:
  java: string
  abra: string
  tmp_dir: string

  input_bams:
    type:
      type: array
      items: File
    inputBinding:
      prefix: --in
      itemSeparator: ','
    secondaryFiles:
    - ^.bai

  patient_id:
    type: string

  working_directory:
    type: string
    inputBinding:
      prefix: --working

  reference_fasta:
    type: string
    inputBinding:
      prefix: --ref

  targets:
    type: File
    inputBinding:
      prefix: --targets

  threads:
    type: int
    inputBinding:
      prefix: --threads

  kmer:
    type: string
    inputBinding:
      prefix: --kmer

  mad:
    type: int
    inputBinding:
      prefix: --mad

  out:
    type:
      type: array
      items: string
    inputBinding:
      itemSeparator: ','
      prefix: --out

outputs:

  bams:
    type: File[]
    outputBinding:
      # Todo: Only specify in one place.
      glob: '*_IR.bam'
