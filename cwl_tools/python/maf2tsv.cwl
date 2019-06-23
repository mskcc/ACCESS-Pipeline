cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1

#baseCommand: [ACCESS_filters]
arguments:
- python
- $('/home/jayakumg/software/dev/cwl/cwl-impact/ACCESS-DMP-VC/python_tools/workflow_tools/maf2tsv.py')

inputs:

  collated_maf:
    type: File
    inputBinding:
      prefix: --anno_maf

  canonical_transcript_reference_file:
    type: File
    inputBinding:
      prefix: --canonical_tx_ref

  outdir:
    type: string?
    inputBinding:
      prefix: --outdir

  title_file:
    type: File
    inputBinding:
      prefix: --title_file

  project_name:
    type: string?
    inputBinding:
      prefix: --project_name


outputs:
  # out_dir:
  #   type: Directory
  #   outputBinding:
  #     glob: Final_Variants

  filtered_exonic:
    type: File
    outputBinding:
      glob: '*_ExonicFiltered.txt'

  dropped_exonic:
    type: File
    outputBinding:
      glob: '*_ExonicDropped.txt'

  filtered_silent:
    type: File
    outputBinding:
      glob: '*_SilentFiltered.txt'

  dropped_silent:
    type: File
    outputBinding:
      glob: '*_SilentDropped.txt'

  filtered_nonpanel:
    type: File
    outputBinding:
      glob: '*_NonPanelFiltered.txt'

  dropped_nonpanel:
    type: File
    outputBinding:
      glob: '*_NonPanelDropped.txt'

#   outputs:
#   out: Directory
# expression: |
#   ${
#     return {"out": {
#       "class": "Directory", 
#       "basename": "my_directory_name",
#       "listing": [inputs.file1, inputs.file2]
#     } };
#   }