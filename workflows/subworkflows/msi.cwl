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

  msisensor_allele_counts:
    type: Directory

  project_name_msi: string?
  coverage_data: Directory?
  outfile: string?


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
  msisensor_dis:
    type: File[]
    outputSource: msisensor/msisensor_dis
  msisensor_stdout:
    type: stdout
    outputSource: msisensor/standard_out
  msisensor_stderr:
    type: stderr
    outputSource: msisensor/standard_err

  distance_vectors:
    type: File
    outputSource: admie/distance_vectors
  admie_results:
    type: File
    outputSource: admie/results
  plots:
    type: File[]
    outputSource: admie/plots
  admie_stdout:
    type: stdout
    outputSource: admie/standard_out
  admie_stderr:
    type: stdout
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
      msisensor_main,
      msisensor_somatic,
      msisensor_germline,
      msisensor_dis,
      standard_out,
      standard_err
    ]
    scatter: [sample_name, tumor_bams, normal_bams]
    scatterMethod: dotproduct

  admie:
    run: ../../cwl_tools/msi/admie.cwl
    in:
      admie_script: admie_script
      file_path: file_path
      project_name_msi: project_name_msi
      msisensor_allele_counts: msisensor_allele_counts
      model: model
      coverage_data: coverage_data
      outfile: outfile
    out: [
      distance_vectors,
      results,
      plots,
      standard_out,
      standard_err
    ]
