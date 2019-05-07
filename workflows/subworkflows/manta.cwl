cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_tools/schemas.yaml

inputs:

  # Todo: what to do with these?
  project_name: string
  version: string

  sample_id: string[]

  tumor_bams:
    type: File[]
    secondaryFiles: [^.bai]

  normal_bams:
    type: File[]
    secondaryFiles: [^.bai]

  reference_fasta:
    type: File
    secondaryFiles: [.fai]

  run_tools: ../../resources/run_tools/schemas.yaml#sv_run_tools

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
      run_tools: run_tools
      sample_id: sample_id
      sv_repo:
        valueFrom: $(inputs.run_tools.sv_repo)
      manta:
        valueFrom: $(inputs.run_tools.manta)
      tumor_sample: tumor_bams
      normal_sample: normal_bams
      reference_fasta: reference_fasta
    scatter: [sample_id, tumor_sample, normal_sample]
    scatterMethod: dotproduct
    out: [sv_vcf, sv_directory]

  annotate_manta:
    run: ../../cwl_tools/manta/manta_annotation.cwl
    in:
      run_tools: run_tools
      sv_repo:
        valueFrom: $(inputs.run_tools.sv_repo)
      manta:
        valueFrom: $(inputs.run_tools.manta)
      vcf: manta/sv_vcf
      sample_id: sample_id
      output_dir:
        valueFrom: $('.')
      reference_fasta: reference_fasta
    scatter: [vcf, sample_id]
    scatterMethod: dotproduct
    out: [sv_file_annotated]
