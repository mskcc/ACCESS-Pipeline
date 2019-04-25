cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    ramMin: 16000

arguments:
- $(inputs.sv_repo + '/scripts/iAnnotateSV.sh')

inputs:

  sv_repo: Directory

  vcf:
    type: File
    inputBinding:
      position: 1

  sample_id:
    type: File
    inputBinding:
      position: 2

  output_dir:
    type: string
    inputBinding:
      position: 3

  manta:
    type: Directory
    inputBinding:
      position: 4

  reference_fasta:
    type: File
    inputBinding:
      position: 5

outputs:

  sv_file_anotated:
    type: File
    outputBinding:
      glob: $(inputs.sample_id + '_Annotated_Evidence.txt')
