#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

baseCommand: [fingerprinting]

requirements:
  InlineJavascriptRequirement: {}

inputs:
  output_directory:
    type: string
    inputBinding:
      prefix: -o

  waltz_directory:
    type: Directory
    inputBinding:
      prefix: -w

  FP_config_file:
    type: File
    inputBinding:
      prefix: -c

  expected_match_file:
    type: File?
    inputBinding:
      prefix: -e

outputs:
  FP_counts_file:
    type: File
    outputBinding:
      glob: $('./FPResults/FP_counts.txt')

  FP_Geno_file:
    type: File
    outputBinding:
      glob: $('./FPResults/FP_Geno.txt')

  FP_mAF_file:
    type: File
    outputBinding:
      glob: $('./FPResults/FP_mAF.txt')

  FPFigures_file:
    type: File
    outputBinding:
      glob: $('./FPResults/FPFigures.pdf')

  Geno_compare_file:
    type: File
    outputBinding:
      glob: $('./FPResults/Geno_compare.txt')

  majorContaminationPlot_file:
    type: File
    outputBinding:
      glob: $('./FPResults/MajorContaminationRate.pdf')

  minorContaminationPlot_file:
    type: File
    outputBinding:
      glob: $('./FPResults/MinorContaminationRate.pdf')

  minorContamination_file:
    type: File
    outputBinding:
      glob: $('./FPResults/majorContamination.txt')

  minorContamination_file:
    type: File
    outputBinding:
      glob: $('./FPResults/minorContamination.txt')

  selectFPComparePlot_file:
    type: File
    outputBinding:
      glob: $('./FPResults/Selectfpcompare.pdf')