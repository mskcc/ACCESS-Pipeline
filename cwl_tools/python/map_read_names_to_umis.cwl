#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

inputs:
  read_names:
    type: File

baseCommand: [map_read_names_to_umis]

arguments:
  - $( inputs.read_names )
  - $( inputs.read_names.basename.replace("_readNames.bed", "_Duplex_UMI_for_readNames.fastq") )

outputs:
  annotated_fastq:
    type: File
    outputBinding:
      glob: $( inputs.read_names.basename.replace("_readNames.bed", "_Duplex_UMI_for_readNames.fastq") )
