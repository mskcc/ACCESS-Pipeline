cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    ramMin: 16000

arguments:
- Rscript
- $(inputs.sv_repo + '/scripts/manta_sample.R')

inputs:

  sv_repo:
    type: Directory
    inputBinding:
      position: 1

  tumor_sample:
    type: File
    inputBinding:
      prefix: --tumor

  normal_sample:
    type: File
    inputBinding:
      prefix: --normal

  output_directory:
    type: Directory
    default: .
    inputBinding:
      prefix: --output

  reference_fasta:
    type: File
    inputBinding:
      prefix: --fasta

  manta:
    type: Directory
    inputBinding:
      prefix: --manta

outputs:

  sv_file:
    type: File
    outputBinding:
      glob: 'results/variants/somaticSV.vcf.gz'

  sv_results:
    type: Directory
    glob: *
