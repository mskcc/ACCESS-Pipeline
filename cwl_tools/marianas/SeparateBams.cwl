cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java_8)
- -server
- -Xms8g
- -Xmx8g
- -cp
- $(inputs.marianas_path)
- org.mskcc.marianas.umi.duplex.postprocessing.SeparateBams

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 1
    outdirMax: 20000

inputs:
  java_8: string
  marianas_path: string

  collapsed_bam:
    type: File
    inputBinding:
      # Todo:
      position: 999

outputs:

  simplex_bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.collapsed_bam.basename.replace('.bam', '-simplex.bam'))

  duplex_bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.collapsed_bam.basename.replace('.bam', '-duplex.bam'))
