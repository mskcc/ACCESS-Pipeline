#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [combine_qc_pdfs]

inputs:

  title_page:
    type: File
    inputBinding:
      position: 1

  read_counts:
    type: File
    inputBinding:
      position: 2

  align_rate:
    type: File
    inputBinding:
      position: 3

  on_target_rate:
    type: File
    inputBinding:
      position: 4

  mean_cov:
    type: File
    inputBinding:
      position: 5

  gc_cov_each_sample:
    type: File
    inputBinding:
      position: 6

  insert_sizes:
    type: File
    inputBinding:
      position: 7

  coverage_per_interval:
    type: File
    inputBinding:
      position: 8

  family_types:
    type: File
    inputBinding:
      position: 9

  family_sizes_all:
    type: File
    inputBinding:
      position: 10

  family_sizes_simplex:
    type: File
    inputBinding:
      position: 11

  family_sizes_duplex:
    type: File
    inputBinding:
      position: 12

  noise_alt_percent:
    type: File
    inputBinding:
      position: 13

  noise_contributing_sites:
    type: File
    inputBinding:
      position: 14

  fingerprinting_qc:
    type: File
    inputBinding:
      position: 15

  gender_check:
    type: File
    inputBinding:
      position: 16

  pipeline_inputs:
    type: File
    inputBinding:
      position: 17

outputs:

  combined_qc:
    type: File
    outputBinding:
      glob: 'main_qc.pdf'
