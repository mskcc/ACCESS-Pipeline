#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1
- class: InitialWorkDirRequirement
  listing:
  - entry: $(inputs.family_sizes)
  - entry: $(inputs.family_types_A)
  - entry: $(inputs.family_types_B)

baseCommand: qc_wrapper

inputs:

  family_sizes: File
  family_types_A: File
  family_types_B: File

  title_file:
    type: File
    inputBinding:
      prefix: -t

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

outputs:

  qc_pdf:
    type: File
    outputBinding:
      # todo: find pdfs explicitly
      glob: '*.pdf'
