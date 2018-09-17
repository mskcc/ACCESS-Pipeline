#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1

baseCommand: tables_module

inputs:

  standard_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: -swa

  unfiltered_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: -mua

  simplex_waltz_metrics_pool_a:
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

  simplex_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: -msb

  duplex_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: -mdb

outputs:

  tables:
    type: Directory
    outputBinding:
      glob: '.'
