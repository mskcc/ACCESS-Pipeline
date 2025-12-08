cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    outdirMin: 13000
    tmpdirMin: 32000
  InitialWorkDirRequirement:
    listing: [$(inputs.bam)]

baseCommand: [samtools, index]

inputs:

  bam:
    type: File
    inputBinding:
      position: 2
      valueFrom: $(self.basename)
    label: Input bam file.

outputs:

  indexed_bam:
    type: File
    secondaryFiles: .bai
    outputBinding:
      glob: $(inputs.bam.basename)
