cwlVersion: v1.0

class: CommandLineTool

requirements:
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_tools/schemas.yaml

baseCommand: find_hotspots_in_normals

inputs:

  run_tools: ../../resources/run_tools/schemas.yaml#run_tools

  java:
    type: string
    inputBinding:
      prefix: --java

  bioinfo_utils:
    type: File
    inputBinding:
      prefix: --bioinfo_utils

  sample_ids:
    type: string[]
    inputBinding:
      prefix: --sample_ids

  patient_ids:
    type: string[]
    inputBinding:
      prefix: --patient_ids

  sample_classes:
    type: string[]
    inputBinding:
      prefix: --sample_classes

  unfiltered_pileups:
    type: File[]
    inputBinding:
      prefix: --unfiltered_pileups

  duplex_pileups:
    type: File[]
    inputBinding:
      prefix: --duplex_pileups

  hotspot_list:
    type: File
    inputBinding:
      prefix: --hotspot_list

outputs:

  hotspots_in_normals_data:
    type: File
    outputBinding:
      glob: 'hotspots-in-normals.txt'

  hotspots_in_normals_table_pdf:
    type: File
    outputBinding:
      glob: 'hotspots_in_normals.pdf'
