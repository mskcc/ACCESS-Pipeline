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
      - $import: ../../resources/run_params/ACCESS_copynumber_run_params.yaml

inputs:

  cnv_params: ../../resources/run_params/ACCESS_copynumber_run_params.yaml

  tumor_sample_list:
    type: File
#    secondaryFiles: [^.bai]
  normal_sample_list:
    type: File

  targets_coverage_bed: File
  targets_coverage_annotation: File
  reference_fasta: File

outputs:
#check this with example output JIRA
    tumors_covg:
        type: File
        outputSource: cnv/t_covg_output
    normals_covg:
        type: File
        outputSource: cnv/n_covg_output
    loess_tumors:
        type: File
        outputSource: cnv/t_loess_output
    loess_normals:
        type: File
        outputSource: cnv/n_loess_output
    normal_loess_pdf:
        type:File
        outputSource: cnv/n_loess_pdf_output
    tumor_loess_pdf:
        type: File
        outputSource: cnv/t_loess_pdf_output
    genes_file:
        type: File
        outputSource: cnv/genes_output
    probes_file:
        type: File
        outputSource: cnv/probes_output
    intragenic_file:
        type: File
        outputSource: cnv/intragenic_output

    copy_pdf:
        type: File
        outputSource: cnv/copy_pdf_output

    #include seg files?

steps:

  cnv:
    run: ../../cwl_tools/cnv/cnv.cwl
    in:
      cnv_params: cnv_params
      reference_sequence: reference_fasta
      tumor_sample_list: tumor_sample_list
      tumor_sample_list: normal_sample_list
      bed_file: bed_file
      targets_file: targets_file

      threads:
        valueFrom: $(inputs.cnv_params.threads)

    out: [t_covg_output, n_covg_output, t_loess_output, n_loess_output, t_loess_pdf_output, n_loess_pdf_output, genes_output, probes_output, intragenic_output, copy_pdf_output]
