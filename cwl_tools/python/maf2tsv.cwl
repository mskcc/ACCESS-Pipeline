cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1

baseCommand: [maf2tsv]

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

  filtered_exonic:
    type: File
    outputBinding:
      glob: '*_ExonicFiltered.pre_traceback.txt'

  dropped_exonic:
    type: File
    outputBinding:
      glob: '*_ExonicDropped.pre_traceback.txt'

  filtered_silent:
    type: File
    outputBinding:
      glob: '*_SilentFiltered.pre_traceback.txt'

  dropped_silent:
    type: File
    outputBinding:
      glob: '*_SilentDropped.pre_traceback.txt'

  filtered_exonic_nonpanel:
    type: File
    outputBinding:
      glob: '*_NonPanelExonicFiltered.txt'

  dropped_exonic_nonpanel:
    type: File
    outputBinding:
      glob: '*_NonPanelExonicDropped.txt'

  filtered_silent_nonpanel:
    type: File
    outputBinding:
      glob: '*_NonPanelSilentFiltered.txt'

  dropped_silent_nonpanel:
    type: File
    outputBinding:
      glob: '*_NonPanelSilentDropped.txt'
