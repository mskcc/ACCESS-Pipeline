cwlVersion: v1.0

class: CommandLineTool

baseCommand: print_hotspots_in_normals_table_pdf

inputs:

  table:
    type: File
    inputBinding:
      prefix: --hotspots_table

outputs:

  hotspots_in_normals_table_pdf:
    type: File
    outputBinding:
      glob: 'hotspots_in_normals.pdf'
