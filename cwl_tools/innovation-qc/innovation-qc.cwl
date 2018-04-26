#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

baseCommand: innovation_qc_with_groups.py

inputs:
  standard_waltz_metrics:
    type: Directory
    inputBinding:
      prefix: -sw

  marianas_unfiltered_waltz_metrics:
    type: Directory?
    inputBinding:
      prefix: -mu

  marianas_simplex_duplex_waltz_metrics:
    type: Directory?
    inputBinding:
      prefix: -ms

  marianas_duplex_waltz_metrics:
    type: Directory?
    inputBinding:
      prefix: -md

  title_file:
    type: File
    inputBinding:
      prefix: -t

outputs:
  qc_pdf:
    type: File[]
    outputBinding:
      # todo: find pdfs explicitly
      glob: ${ return '**/**/**/*.pdf' }
