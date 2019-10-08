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
      - $import: ../../resources/run_tools/ACCESS_variants_run_tools.yaml

inputs:

  run_tools: ../../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools

  admie_script: string
  file_path: string
  threads: int

  microsatellites: File
  model: File

  sample_name: string[]

  tumor_bam:
    type: File[]
    secondaryFiles: [^.bai]

  normal_bam:
    type: File[]
    secondaryFiles: [^.bai]

  project_name_msi: string?
  coverage_data: Directory?


outputs:

  msisensor_main:
    type: File[]
    outputSource: msisensor/msisensor_main
  msisensor_somatic:
    type: File[]
    outputSource: msisensor/msisensor_somatic
  msisensor_germline:
    type: File[]
    outputSource: msisensor/msisensor_germline
  msisensor_distribution:
    type: File[]
    outputSource: msisensor/msisensor_distribution
  msisensor_stdout:
    type: File[]
    outputSource: msisensor/standard_out
  msisensor_stderr:
    type: File[]
    outputSource: msisensor/standard_err

  distance_vectors:
    type: File
    outputSource: admie/distance_vectors
  admie_results:
    type: File
    outputSource: admie/admie_results
  plots:
    type: File[]?
    outputSource: admie/plots
  admie_stdout:
    type: File
    outputSource: admie/standard_out
  admie_stderr:
    type: File
    outputSource: admie/standard_err


steps:

  msisensor:
    run: ../../cwl_tools/msi/msisensor.cwl
    in:
      run_tools: run_tools
      msisensor:
        valueFrom: $(inputs.run_tools.msisensor)
      microsatellites: microsatellites
      tumor_bam: tumor_bam
      normal_bam: normal_bam
      sample_name: sample_name
      threads: threads
    out: [
      msisensor_main,
      msisensor_somatic,
      msisensor_germline,
      msisensor_distribution,
      standard_out,
      standard_err
    ]
    scatter: [sample_name, tumor_bam, normal_bam]
    scatterMethod: dotproduct

  admie:
    run: ../../cwl_tools/msi/admie.cwl
    in:
      admie_script: admie_script
      file_path: file_path
      project_name_msi: project_name_msi
      allele_counts_list: msisensor/msisensor_distribution
      model: model
      coverage_data: coverage_data
    out: [
      distance_vectors,
      admie_results,
      plots,
      standard_out,
      standard_err
    ]
