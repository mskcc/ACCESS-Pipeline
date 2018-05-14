#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl

inputs:
  run_tools:
    type:
      type: record
      fields:
        perl_5: string
        java_7: string
        java_8: string
        marianas_path: string
        trimgalore_path: string
        bwa_path: string
        arrg_path: string
        picard_path: string
        gatk_path: string
        abra_path: string
        fx_path: string
        fastqc_path: string?
        cutadapt_path: string?

  samples: ../../resources/schema_defs/Sample.cwl#Sample[]

  tmp_dir: string
  reference_fasta: string

  bqsr__nct: int
  bqsr__rf: string
  bqsr__knownSites_dbSNP:
    type: File
    secondaryFiles:
      - .idx
  bqsr__knownSites_millis:
    type: File
    secondaryFiles:
      - .idx
  print_reads__nct: int
  print_reads__EOQ: boolean
  print_reads__baq: string

outputs:

  output_samples:
    type:
      type: array
      items: ../../resources/schema_defs/Sample.cwl#Sample
    outputSource: parallel_printreads/output_samples

steps:

  parallel_bqsr:
    in:
      run_tools: run_tools
      java:
        valueFrom: ${return inputs.run_tools.java_8}
      gatk:
        valueFrom: ${return inputs.run_tools.gatk_path}
      tmp_dir: tmp_dir

      samples: samples
      bam:
        valueFrom: $(inputs.samples.bam)

      reference_fasta: reference_fasta
      rf: bqsr__rf
      nct: bqsr__nct
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
        tmp_dir: string

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
            tmp_dir: tmp_dir
            java: java
            gatk: gatk

            input_bam: bam

            reference_fasta: reference_fasta
            rf: rf
            nct: nct
            known_sites_1: known_sites_1
            known_sites_2: known_sites_2
            out:
              default: 'recal.matrix'
          out: [recal_matrix]

  parallel_printreads:
    in:
      run_tools: run_tools
      java:
        valueFrom: ${return inputs.run_tools.java_8}
      gatk:
        valueFrom: ${return inputs.run_tools.gatk_path}

      tmp_dir: tmp_dir

      sample: samples
      BQSR: parallel_bqsr/recal_matrix

      nct: print_reads__nct
      EOQ: print_reads__EOQ
      baq: print_reads__baq
      reference_sequence: reference_fasta
    out: [output_samples]
    scatter: [sample, BQSR]
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
        tmp_dir: string
        java: string
        gatk: string

        sample: ../../resources/schema_defs/Sample.cwl#Sample
        BQSR: File

        nct: int
        EOQ: boolean
        reference_sequence: string
        baq: string
      outputs:
        output_samples:
          type: ../../resources/schema_defs/Sample.cwl#Sample
          outputSource: gatk_print_reads/output_sample
      steps:
        gatk_print_reads:
          run: ../../cwl_tools/gatk/PrintReads.cwl
          in:
            tmp_dir: tmp_dir
            java: java
            gatk: gatk

            sample: sample
            input_file:
              valueFrom: $(inputs.sample.ir_bam)

            BQSR: BQSR
            nct: nct
            EOQ: EOQ
            baq: baq
            reference_sequence: reference_sequence
            out:
              valueFrom: ${return inputs.input_file.basename.replace('.bam', '_BR.bam')}
          out: [output_sample]
