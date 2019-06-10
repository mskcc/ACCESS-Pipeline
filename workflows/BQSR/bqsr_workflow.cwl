cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_tools/schemas.yaml
      - $import: ../../resources/run_params/schemas/base_recalibrator.yaml
      - $import: ../../resources/run_params/schemas/print_reads.yaml

inputs:
  run_tools: ../../resources/run_tools/schemas.yaml#run_tools

  bams:
    type: File[]
    secondaryFiles:
      - ^.bai

  reference_fasta: string

  bqsr__knownSites_dbSNP:
    type: File
    secondaryFiles:
      - .idx
  bqsr__knownSites_millis:
    type: File
    secondaryFiles:
      - .idx

  base_recalibrator__params: ../../resources/run_params/schemas/base_recalibrator.yaml#base_recalibrator__params
  print_reads__params: ../../resources/run_params/schemas/print_reads.yaml#print_reads__params

outputs:

  bqsr_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
    outputSource: parallel_printreads/bams

steps:

  parallel_bqsr:
    in:
      run_tools: run_tools
      params: base_recalibrator__params
      java:
        valueFrom: ${return inputs.run_tools.java_7}
      gatk:
        valueFrom: ${return inputs.run_tools.gatk_path}
      bam: bams
      reference_fasta: reference_fasta
      rf:
        valueFrom: $(inputs.params.rf)
      nct:
        valueFrom: $(inputs.params.nct)

      known_sites_1: bqsr__knownSites_dbSNP
      known_sites_2: bqsr__knownSites_millis
    out: [recal_matrix]
    scatter: bam
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
        java: string
        gatk: string
        bam: File
        reference_fasta: string
        rf: string
        nct: int
        known_sites_1: File
        known_sites_2: File
      outputs:
        recal_matrix:
          type: File
          outputSource: bqsr/recal_matrix
      steps:
        bqsr:
          run: ../../cwl_tools/gatk/BaseQualityScoreRecalibration.cwl
          in:
            java: java
            gatk: gatk
            input_bam: bam
            reference_fasta: reference_fasta
            rf: rf
            nct: nct
            known_sites_1: known_sites_1
            known_sites_2: known_sites_2
            out:
              default:
                valueFrom: $(inputs.input_bam.basename + '.recal.matrix')
          out: [recal_matrix]

  parallel_printreads:
    in:
      run_tools: run_tools
      params: print_reads__params
      java:
        valueFrom: ${return inputs.run_tools.java_7}
      gatk:
        valueFrom: ${return inputs.run_tools.gatk_path}

      input_file: bams
      BQSR: parallel_bqsr/recal_matrix

      nct:
        valueFrom: $(inputs.params.nct)
      EOQ:
        valueFrom: $(inputs.params.EOQ)
      baq:
        valueFrom: $(inputs.params.baq)

      reference_sequence: reference_fasta
    out: [bams]
    scatter: [input_file, BQSR]
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
        java: string
        gatk: string
        input_file: File
        BQSR: File
        nct: int
        EOQ: boolean
        reference_sequence: string
        baq: string
      outputs:
        bams:
          type: File
          secondaryFiles:
            - ^.bai
          outputSource: gatk_print_reads/out_bams
      steps:
        gatk_print_reads:
          run: ../../cwl_tools/gatk/PrintReads.cwl
          in:
            java: java
            gatk: gatk
            input_file: input_file
            BQSR: BQSR
            nct: nct
            EOQ: EOQ
            baq: baq
            reference_sequence: reference_sequence
            out:
              valueFrom: ${return inputs.input_file.basename.replace(".bam", "_BR.bam")}
          out: [out_bams]
