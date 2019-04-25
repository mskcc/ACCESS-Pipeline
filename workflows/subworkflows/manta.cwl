cwlVersion: v1.0

class: Workflow

requirements:
  InlineJavaScriptRequirement: {}

inputs:

  sample_id: string[]
  tumor_bams: File[]
  normal_bams: File[]

  reference_fasta: File

  run_tools:
    manta: Directory
    sv_repo: Directory

outputs:

  sv_directory:
    type: Directory[]
    outputSource: manta/sv_directory

  annotated_sv_file:
    type: File[]
    outputSource: annotate_manta/sv_file_annotated

steps:

  manta:
    run: ../../cwl_tools/manta/manta.cwl
    in:
      sv_repo: sv_repo
      manta: manta
      tumor_bams: tumor_bams
      normal_bams: normal_bams
      reference_fasta: reference_fasta
    scatter: [tumor_bams, normal_bams]
    scatterMethod: dotproduct
    out: [sv_vcf, sv_directory]

  annotate_manta:
    run: ../../cwl_tools/manta/annotate_manta.cwl
    in:
      sv_repo: sv_repo
      manta: manta
      vcf: manta/sv_vcf
      sample_id: sample_id
      output_dir:
        valueFrom: $('.')
      reference_fasta: reference_fasta
    scatter: [vcf, sample_id]
    scattterMethod: dotproduct
    out: [sv_file_annotated]
