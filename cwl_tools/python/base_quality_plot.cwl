cwlVersion: v1.0

class: CommandLineTool

baseCommand: [base_quality_plot]

inputs:

  picard_metrics:
    type: Directory
    inputBinding:
      prefix: --picard_metrics_directory

outputs:

  plot:
    type: File
    outputBinding:
      glob: 'base_quality_plot.pdf'
