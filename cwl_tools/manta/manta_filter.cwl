cwlVersion: v1.0

class: CommandLineTool

doc: |
  The purpose of this step is to filter out reads from bams that have terminating INDELs.
  These reads are a new development since upgrading to Abra2, and are not supported by Manta.

requirements:
  ShellCommandRequirement: {}
  ResourceRequirement:
    ramMin: 2000

baseCommand: samtools

arguments:
- view
- -h
- $(inputs.bam)

- shellQuote: false
  valueFrom: $('|')

- awk
- $6!~/^.*.[0-9]+I[0-9]+D$|^.*.[0-9]+D[0-9]+I$|^.*.[0-9]+D[0-9]+I[0-9]+S$|^.*.[0-9]+I[0-9]+D[0-9]+S$/

- shellQuote: false
  valueFrom: $('|')

- samtools
- view
- -b
- '-'

- shellQuote: false
  valueFrom: $('>')

- $(inputs.output_file_name)

inputs:

  bam: File

  output_file_name: string

outputs:

  filtered_bam:
    type: File
    outputBinding:
      glob: $(inputs.output_file_name)
