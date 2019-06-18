cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}

inputs:

  admie_script: string
  file_path: string
  threads: int

  microsatellites: File
  normal_bam: File
  tumor_bam: File
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

  msisensor_outputdir:
    type: Directory[]
    outputSource: msisensor/output_dir
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
    type: File[]
    outputSource: admie/distance_vectors
  admie_results:
    type: File[]
    outputSource: admie/results
  plots:
    type:
      type: array
      items:
        type: array
        items: File
    outputSource: admie/plots
  admie_stdout:
    type: File[]
    outputSource: admie/standard_out
  admie_stderr:
    type: File[]
    outputSource: admie/standard_err


steps:

  msisensor:
    run: ../../cwl_tools/msi/msisensor.cwl
    in:
      microsatellites: microsatellites
      tumor_bam: tumor_bam
      normal_bam: normal_bam
      sample_name: sample_name
      threads: threads
    out: [
      output_dir,
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
      msisensor_allele_counts: msisensor/output_dir
      model: model
      coverage_data: coverage_data
    out: [
      distance_vectors,
      results,
      plots,
      standard_out,
      standard_err
    ]
    scatter: [msisensor_allele_counts]
    scatterMethod: dotproduct
