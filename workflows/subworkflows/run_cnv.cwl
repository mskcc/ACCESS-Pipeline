cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}

inputs:

  tumor_sample_list: File
  normal_sample_list: File
  targets_coverage_bed: File
  targets_coverage_annotation: File
  reference_fasta: File

  project_name: string
  loess_normalize_script: File
  copy_number_script: File
  output: Directory
  threads: int
  qsub: string
  queue: string
  r_path: string

outputs:
#check this with example output JIRA
    tumors_covg:
        type: File
        outputSource: cnv/tumors_covg
    normals_covg:
        type: File
        outputSource: cnv/normals_covg
    loess_tumors:
        type: File
        outputSource: cnv/loess_tumors
    loess_normals:
        type: File
        outputSource: cnv/loess_normals
    normal_loess_pdf:
        type: File
        outputSource: cnv/normal_loess_pdf
    tumor_loess_pdf:
        type: File
        outputSource: cnv/tumor_loess_pdf
    genes_file:
        type: File
        outputSource: cnv/genes_file
    probes_file:
        type: File
        outputSource: cnv/probes_file
    intragenic_file:
        type: File
        outputSource: cnv/intragenic_file

    copy_pdf:
        type: File
        outputSource: cnv/copy_pdf

    #include seg files?

steps:

  cnv:
    run: ../../cwl_tools/cnv/cnv.cwl
    in:
      reference_fasta: reference_fasta
      tumor_sample_list: tumor_sample_list
      normal_sample_list: normal_sample_list
      targets_coverage_bed: targets_coverage_bed
      targets_coverage_annotation: targets_coverage_bed
      project_name: project_name
      loess_normalize_script: loess_normalize_script
      copy_number_script: copy_number_script
      output: output
      threads: threads
      qsub: qsub
      queue: queue
      r_path: r_path

    out: [tumors_covg, normals_covg, loess_tumors, loess_normals, normal_loess_pdf, tumor_loess_pdf, genes_file, probes_file, intragenic_file, copy_pdf]
