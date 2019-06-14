cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  # SchemaDefRequirement:
  #   types:
  #     - $import: ../../resources/run_tools/schemas.yaml

inputs:
  # TODO: remove the following two variables?
  project_name: string
  version: string

  sample_id: string[]

  tumor_bam:
    type: File[]
    secondaryFiles: [^.bai]

  normal_bam:
    type: File[]
    secondaryFiles: [^.bai]

  microsatellites:
    type: File

  threads:
    type: int
  
  model:
    type: File


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
  distance_vectors:
    type: File
    outputSource: admie/distance_vectors
  admie_results:
    type: File
    outputSource: admie/esults
  plots:
    type: File[]
    outputSource: admie/plots


steps:

  msisensor:
    run: ../../cwl_tools/msi/msisensor.cwl
    in:
      tumor_bam: tumor_bam
      normal_bam: normal_bam
      output_file_name:
    out: [msisensor_main, msisensor_somatic, msisensor_germline, msisensor_dis]
    scatter: [sample_id, tumor_bams, normal_bams]
    scatterMethod: dotproduct

  admie:
    run: ../../cwl_tools/msi/admie.cwl
    in:
      msisensor_allele_counts: msisensor
      model: model
    out: [distance_vectors, results, plots]
