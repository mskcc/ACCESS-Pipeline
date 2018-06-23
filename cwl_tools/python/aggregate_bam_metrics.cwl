#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1
- class: InitialWorkDirRequirement
  listing: $(inputs.waltz_input_files.listing)


baseCommand: [aggregate_bam_metrics.sh]

inputs:

  waltz_input_files: Directory

  title_file:
    type: File
    inputBinding:
      position: 2

outputs:

  output_dir:
    type: Directory
    outputBinding:
      glob: .
