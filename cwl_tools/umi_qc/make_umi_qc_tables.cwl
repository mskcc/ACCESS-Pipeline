#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [make_umi_qc_tables.sh]

requirements:
- class: InlineJavascriptRequirement
#- class: InitialWorkDirRequirement
#  listing: # $(inputs.folders)
#  - entry: $(inputs.folders[0])

inputs:

  A_on_target_positions:
    type: File
    inputBinding:
      position: 1

  B_on_target_positions:
    type: File
    inputBinding:
      position: 2

  folders:
    type: Directory[]
    inputBinding:
      position: 3

outputs:

  cluster_sizes:
    type: File
    outputBinding:
      glob: 'cluster-sizes.txt'

  cluster_sizes_post_filtering:
    type: File
    outputBinding:
      glob: 'cluster-sizes-post-filtering.txt'

  clusters_per_position:
    type: File
    outputBinding:
        glob: 'clusters-per-position.txt'

  clusters_per_position_post_filtering:
    type: File
    outputBinding:
      glob: 'clusters-per-position-post-filtering.txt'

  family_types_A:
    type: File
    outputBinding:
      glob: 'family-types-A.txt'

  family_types_B:
    type: File
    outputBinding:
      glob: 'family-types-B.txt'
