cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SubworkflowFeatureRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_tools/schemas.yaml
      - $import: ../resources/run_params/schemas/find_covered_intervals.yaml
      - $import: ../resources/run_params/schemas/abra.yaml
      - $import: ../resources/run_params/schemas/fix_mate_information.yaml
      - $import: ../resources/run_params/schemas/base_recalibrator.yaml
      - $import: ../resources/run_params/schemas/print_reads.yaml

inputs:
  run_tools: ../resources/run_tools/schemas.yaml#run_tools

  bams:
    type:
      type: array
      items: File
    secondaryFiles:
      - ^.bai
  patient_id: string

  tmp_dir: string
  reference_fasta: string

  find_covered_intervals__params: ../resources/run_params/schemas/find_covered_intervals.yaml#find_covered_intervals__params
  abra__params: ../resources/run_params/schemas/abra.yaml#abra__params
  fix_mate_information__params: ../resources/run_params/schemas/fix_mate_information.yaml#fix_mate_information__params
  base_recalibrator__params: ../resources/run_params/schemas/base_recalibrator.yaml#base_recalibrator__params
  print_reads__params: ../resources/run_params/schemas/print_reads.yaml#print_reads__params

  bqsr__knownSites_dbSNP:
    type: File
    secondaryFiles:
      - .idx
  bqsr__knownSites_millis:
    type: File
    secondaryFiles:
      - .idx

outputs:

  standard_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
    outputSource: BQSR_workflow/bqsr_bams

  covint_list:
    type: File
    outputSource: ABRA_workflow/covint_list

  covint_bed:
    type: File
    outputSource: ABRA_workflow/covint_bed

steps:

  ABRA_workflow:
    run: ABRA/abra_workflow.cwl
    in:
      run_tools: run_tools
      bams: bams
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      patient_id: patient_id
      find_covered_intervals__params: find_covered_intervals__params
      abra__params: abra__params
      fix_mate_information__params: fix_mate_information__params
    out: [ir_bams, covint_list, covint_bed]

  BQSR_workflow:
    run: BQSR/bqsr_workflow.cwl
    in:
      run_tools: run_tools
      bams: ABRA_workflow/ir_bams
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      base_recalibrator__params: base_recalibrator__params
      print_reads__params: print_reads__params
    out: [bqsr_bams]
