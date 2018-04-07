#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:

  tmp_dir: string
  reference_fasta: string

  bams:
    type:
      type: array
      items: File
    secondaryFiles:
      - ^.bai

  patient_id: string

  fci__minbq: int
  fci__minmq: int
  fci__cov: int
  fci__rf: string
  fci__intervals: string[]?

  abra__kmers: string
  abra__scratch: string
  abra__mad: int

  fix_mate_information__sort_order: string
  fix_mate_information__validation_stringency: string
  fix_mate_information__compression_level: int
  fix_mate_information__create_index: boolean

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

  standard_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
    outputSource: parallel_printreads/bams

  standard_bais:
    type: File[]
    outputSource: parallel_printreads/bais

  covint_list:
    type: File
    outputSource: find_covered_intervals/fci_list

  covint_bed:
    type: File
    outputSource: list2bed/output_file

steps:

  find_covered_intervals:
    run: ../cwl_tools/gatk/FindCoveredIntervals.cwl
    in:
      bams: bams
      patient_id: patient_id
      reference_sequence: reference_fasta
      min_base_quality: fci__minbq
      min_mapping_quality: fci__minmq
      coverage_threshold: fci__cov
      read_filters: fci__rf
      intervals: fci__intervals
      out:
        valueFrom: ${return inputs.patient_id + ".fci.list"}
    out: [fci_list]

  list2bed:
    run: ../cwl_tools/python/list2bed.cwl
    in:
      input_file: find_covered_intervals/fci_list
      output_filename:
        valueFrom: ${return inputs.input_file.basename.replace(".list", ".bed")}
    out: [output_file]

  abra:
    run: ../cwl_tools/abra/abra.cwl
    in:
      input_bams: bams
      targets: list2bed/output_file
      scratch_dir: abra__scratch
      patient_id: patient_id
      reference_fasta: reference_fasta
      kmer: abra__kmers
      mad: abra__mad
      threads:
        valueFrom: ${ return 12 }
      # Todo: Find a cleaner way
      working_directory:
        valueFrom: ${return inputs.scratch_dir + '__' + inputs.patient_id + '_' + Math.floor(Math.random() * 99999999); }
      out:
        valueFrom: |
          ${return inputs.input_bams.map(function(b){ return b.basename.replace(".bam", "_IR.bam")})}
    out:
      [bams]

  parallel_fixmate:
    in:
      bam: abra/bams
      tmp_dir: tmp_dir
      sort_order: fix_mate_information__sort_order
      create_index: fix_mate_information__create_index
      compression_level: fix_mate_information__compression_level
      validation_stringency: fix_mate_information__validation_stringency
    out: [bams]
    scatter: [bam]
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
        bam: File
        tmp_dir: string
        sort_order: string
        create_index: boolean
        compression_level: int
        validation_stringency: string
      outputs:
        bams:
          type: File
          outputSource: picard_fixmate_information/bam
      steps:
        picard_fixmate_information:
          run: ../cwl_tools/picard/FixMateInformation.cwl
          in:
            input_bam: bam
            tmp_dir: tmp_dir
            sort_order: sort_order
            create_index: create_index
            compression_level: compression_level
            validation_stringency: validation_stringency
          out: [bam]

  parallel_bqsr:
    in:
      bam: parallel_fixmate/bams
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
          run: ../cwl_tools/gatk/BaseQualityScoreRecalibration.cwl
          in:
            input_bam: bam
            reference_fasta: reference_fasta
            rf: rf
            nct: nct
            known_sites_1: known_sites_1
            known_sites_2: known_sites_2
            out:
              default: "recal.matrix"
          out: [recal_matrix]

  parallel_printreads:
    in:
      input_file: parallel_fixmate/bams
      BQSR: parallel_bqsr/recal_matrix
      nct: print_reads__nct
      EOQ: print_reads__EOQ
      baq: print_reads__baq
      reference_sequence: reference_fasta
    out: [bams, bais]
    scatter: [input_file, BQSR]
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
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
        bais:
          type: File
          outputSource: gatk_print_reads/out_bais
      steps:
        gatk_print_reads:
          run: ../cwl_tools/gatk/PrintReads.cwl
          in:
            input_file: input_file
            BQSR: BQSR
            nct: nct
            EOQ: EOQ
            baq: baq
            reference_sequence: reference_sequence
            out:
              valueFrom: ${return inputs.input_file.basename.replace(".bam", "_BR.bam")}
          out: [out_bams, out_bais]
