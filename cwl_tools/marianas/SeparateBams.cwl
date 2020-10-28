cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java_8)
- -server
- -Xms8g
- -Xmx8g
- -cp
- $(inputs.marianas_path)
- org.mskcc.marianas.umi.duplex.postprocessing.SeparateBams

requirements:
  - class: SchemaDefRequirement
    types:
      - $import: ../../resources/schemas/bam_sample.yaml
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 1
    outdirMax: 20000

inputs:
  java_8: string
  marianas_path: string

  add_rg_SM: string
  patient_id: string
  sample_class: string

  collapsed_bam:
    type: File
    inputBinding:
      # Todo:
      position: 999

outputs:

  simplex_bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.collapsed_bam.basename.replace('.bam', '-simplex.bam'))

  simplex_bam_record:
    type: ../../resources/schemas/bam_sample.yaml#bam_sample
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.collapsed_bam.basename.replace('.bam', '-simplex.bam'))
      outputEval: |-
        ${
          return {
            'file': self,
            'sampleId': inputs.add_rg_SM,
            'patientId': inputs.patient_id,
            'tumorOrNormal': inputs.sample_class
          }
        }

  duplex_bam:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.collapsed_bam.basename.replace('.bam', '-duplex.bam'))

  duplex_bam_record:
    type: ../../resources/schemas/bam_sample.yaml#bam_sample
    secondaryFiles: [^.bai]
    outputBinding:
      glob: $(inputs.collapsed_bam.basename.replace('.bam', '-duplex.bam'))
      outputEval: |-
        ${
          return {
            'file': self,
            'sampleId': inputs.add_rg_SM,
            'patientId': inputs.patient_id,
            'tumorOrNormal': inputs.sample_class
          }
        }
