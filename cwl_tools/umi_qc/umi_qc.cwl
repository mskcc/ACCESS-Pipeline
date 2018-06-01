#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [plot_umi_qc.r]

requirements:
  InlineJavascriptRequirement: {}

# cluster-sizes.txt
# cluster-sizes-post-filtering.txt
# clusters-per-position.txt
# clusters-per-position-post-filtering.txt

# Outputs:
# cluster-sizes.pdf
# cluster-sizes-post-filtering.pdf
# clusters-per-position.pdf
# clusters-per-position-post-filtering.pdf

inputs:

  cluster_sizes:
    type: File
    inputBinding:
      position: 1

  cluster_sizes_post_filtering:
    type: File
    inputBinding:
      position: 2

  clusters_per_position:
    type: File
    inputBinding:
      position: 3

  clusters_per_position_post_filtering:
    type: File
    inputBinding:
      position: 4

outputs:

  plots:
    type: File[]
    outputBinding:
      glob: $('*.pdf')
