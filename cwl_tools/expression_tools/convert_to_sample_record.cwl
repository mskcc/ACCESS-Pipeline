#!toil-cwl-runner

# This tool returns a CWL record object,
# which contains a Bam file, and associated metadata

cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 2000
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/bam_sample.yaml

inputs:

    bam: File
    add_rg_SM: string
    patient_id: string
    sample_class: string

outputs:

  sample_record: ../../resources/schemas/bam_sample.yaml#bam_sample

expression: |
  ${
    return {
      'file': inputs.bam,
      'sampleId': inputs.add_rg_SM,
      'patientId': inputs.patient_id,
      'tumorOrNormal': inputs.sample_class
    }
  }
