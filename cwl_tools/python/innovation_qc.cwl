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

  inputs_yaml:
    type: File
    inputBinding:
      prefix: -y

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

  read_counts:
    type: File
    outputBinding:
      glob: 'read_counts.pdf'

  align_rate:
    type: File
    outputBinding:
      glob: 'align_rate.pdf'

  mean_cov:
    type: File
    outputBinding:
      glob: 'mean_cov.pdf'

  on_target_rate:
    type: File
    outputBinding:
      glob: 'on_target_rate.pdf'

  gc_cov_each_sample:
    type: File
    outputBinding:
      glob: 'gc_cov_each_sample.pdf'

  insert_sizes:
    type: File
    outputBinding:
      glob: 'insert_sizes.pdf'

  coverage_per_interval:
    type: File
    outputBinding:
      glob: 'coverage_per_interval.pdf'

  title_page:
    type: File
    outputBinding:
      glob: 'title_page.pdf'

  pipeline_inputs:
    type: File
    outputBinding:
      glob: 'pipeline_inputs.pdf'

  family_types:
    type: File
    outputBinding:
      glob: 'family_types.pdf'

  family_sizes_all:
    type: File
    outputBinding:
      glob: 'family_sizes_all.pdf'

  family_sizes_simplex:
    type: File
    outputBinding:
      glob: 'family_sizes_simplex.pdf'

  family_sizes_duplex:
    type: File
    outputBinding:
      glob: 'family_sizes_duplex.pdf'
