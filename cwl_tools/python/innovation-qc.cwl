#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 4000
    coresMin: 1

baseCommand: qc_wrapper

inputs:
  standard_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: -swa

  unfiltered_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: -mua

  simplex_duplex_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: -msa

  duplex_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: -mda

  standard_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: -swb

  unfiltered_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: -mub

  simplex_duplex_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: -msb

  duplex_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: -mdb

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
