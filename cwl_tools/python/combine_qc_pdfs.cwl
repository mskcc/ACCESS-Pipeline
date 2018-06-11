#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [combine_qc_pdfs]

requirements:
  InlineJavascriptRequirement: {}

inputs:
  umi_qc:
    type: File[]
    inputBinding:
      prefix: --umi_qc

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

outputs:

  combined_qc:
    type: File
    outputBinding:
      glob: $('all_qc.pdf')
