#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [combine_qc_pdfs]

requirements:
  InlineJavascriptRequirement: {}

inputs:

  std_qc:
    type: File
    inputBinding:
      prefix: --std_qc

  noise_alt_percent:
    type: File
    inputBinding:
      prefix: --noise_alt_percent

  noise_contributing_sites:
    type: File
    inputBinding:
      prefix: --noise_contributing_sites

  fingerprinting_qc:
    type: File
    inputBinding:
      prefix: --fingerprinting_qc

  gender_check:
    type: File?
    inputBinding:
      prefix: --gender_check

outputs:

  combined_qc:
    type: File
    outputBinding:
      glob: 'main_qc.pdf'
