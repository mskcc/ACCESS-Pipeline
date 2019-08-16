cwlVersion: v1.0

class: CommandLineTool

baseCommand: plot_hotspots_in_normals.r

requirements:
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.hotspots_in_normals_data)
        writable: false

inputs:

  hotspots_in_normals_data: File

outputs:

  hotspots_in_normals_plot:
    type: File
    outputBinding:
      glob: 'hotspots_in_normals.pdf'
