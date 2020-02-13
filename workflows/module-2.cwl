cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SubworkflowFeatureRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/schemas/collapsing_tools.yaml
      - $import: ../resources/schemas/params/abra.yaml
      - $import: ../resources/schemas/params/print_reads.yaml
      - $import: ../resources/schemas/params/base_recalibrator.yaml
      - $import: ../resources/schemas/params/fix_mate_information.yaml
      - $import: ../resources/schemas/params/find_covered_intervals.yaml

inputs:
  run_tools: ../resources/schemas/collapsing_tools.yaml#run_tools
  abra__params: ../resources/schemas/params/abra.yaml#abra__params
  print_reads__params: ../resources/schemas/params/print_reads.yaml#print_reads__params
  base_recalibrator__params: ../resources/schemas/params/base_recalibrator.yaml#base_recalibrator__params
  fix_mate_information__params: ../resources/schemas/params/fix_mate_information.yaml#fix_mate_information__params
  find_covered_intervals__params: ../resources/schemas/params/find_covered_intervals.yaml#find_covered_intervals__params

  patient_id: string
  reference_fasta: string

  bams:
    type: File[]
    secondaryFiles:
      - ^.bai

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

  recalibrated_scores_matrix:
    type: File[]
    outputSource: BQSR_workflow/recalibrated_scores_matrix

steps:

  ABRA_workflow:
    run: ABRA/abra_workflow.cwl
    in:
      run_tools: run_tools
      bams: bams
      reference_fasta: reference_fasta
      patient_id: patient_id
      find_covered_intervals__params: find_covered_intervals__params
      fci__basq_fix:
        valueFrom: $(false)
      abra__params: abra__params
      fix_mate_information__params: fix_mate_information__params
    out: [ir_bams, covint_list, covint_bed]

  BQSR_workflow:
    run: BQSR/bqsr_workflow.cwl
    in:
      run_tools: run_tools
      bams: ABRA_workflow/ir_bams
      reference_fasta: reference_fasta
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      base_recalibrator__params: base_recalibrator__params
      print_reads__params: print_reads__params
    out: [bqsr_bams, recalibrated_scores_matrix]
