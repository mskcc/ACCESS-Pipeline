cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    coresMin: 8
    ramMin: 16000
    outdirMax: 5000

arguments:
- Rscript
- $(inputs.sv_repo.path + '/scripts/manta_sample.R')

inputs:

  #r_path: string
  sv_repo: Directory
  sample_id: string

  tumor_sample:
    type: File
    secondaryFiles: [.bai]
    inputBinding:
      prefix: --tumor

  normal_sample:
    type: File
    secondaryFiles: [.bai]
    inputBinding:
      prefix: --normal

  output_directory:
    type: string
    default: .
    inputBinding:
      prefix: --output

  reference_fasta:
    type: File
    secondaryFiles: [.fai]
    inputBinding:
      prefix: --fasta

  manta:
    type: Directory
    inputBinding:
      prefix: --manta

outputs:

  sv_vcf:
    type: File
    outputBinding:
      glob: 'results/variants/somaticSV.vcf.gz'

  sv_directory:
    type: Directory
    outputBinding:
      glob: '.'
      outputEval: |
        ${
          self[0].basename = inputs.sample_id;
          return self[0]
        }
