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

  marianas_waltz_metrics:
    type: Directory?
    inputBinding:
      prefix: -mw

  fulcrum_waltz_metrics:
    type: Directory?
    inputBinding:
      prefix: -fw

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