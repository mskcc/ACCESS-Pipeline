cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}

inputs:

  coverage_script: File
  copy_number_script: File
  loess_normalize_script: File

  tumor_sample_list: File
  normal_sample_list: File
  targets_coverage_bed: File
  targets_coverage_annotation: File
  reference_fasta: File

  project_name: string
  loess_normalize_script: File
  copy_number_script: File
  threads: int

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

  coverage:
    run: ../../cwl_tools/cnv/coverage.cwl
    in:
      coverage_script: coverage_script
      project_name: project_name
      threads: threads
      tumor_sample_list: tumor_sample_list
      normal_sample_list: normal_sample_list
      targets_coverage_bed: targets_coverage_bed
      reference_fasta: reference_fasta

    out: [tumors_covg, normals_covg, bam_list]

  loess_tumor:
    run: ../../cwl_tools/cnv/loess.cwl
    in:
      loess_normalize_script: loess_normalize_script
      project_name: project_name
      coverage_file: tumors_covg
      targets_coverage_annotation: targets_coverage_annotation

    out: [loess_tumors, tumor_loess_pdf]
      
  loess_normal:
    run: ../../cwl_tools/cnv/loess.cwl
    in:
      loess_normalize_script: loess_normalize_script
      project_name: project_name
      coverage_file: normals_covg
      targets_coverage_annotation: targets_coverage_annotation

    out: [loess_normals, normal_loess_pdf]

  copy_number:
    run: ../../cwl_tools/cnv/copynumber.cwl
    in:
      copy_number_script: copy_number_script
      project_name: project_name
      loess_normals: loess_normals
      loess_tumors: loess_tumors
      targets_coverage_annotation: targets_coverage_annotation

    out: [genes_file, probes_file, intragenic_file, intragenic_file]

