#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}

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

  bams:
    type:
      type: array
      items: File
    secondaryFiles:
      - ^.bai

  tmp_dir: string
  reference_fasta: string
  patient_id: string

  fci__minbq: int
  fci__minmq: int
  fci__cov: int
  fci__rf: string[]
  fci__intervals: string[]?
  fci__basq_fix: boolean?
  abra__kmers: string
  abra__scratch: string
  abra__mad: int
  fix_mate_information__sort_order: string
  fix_mate_information__validation_stringency: string
  fix_mate_information__compression_level: int
  fix_mate_information__create_index: boolean

outputs:

  ir_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
    outputSource: parallel_fixmate/bams

  covint_list:
    type: File
    outputSource: find_covered_intervals/fci_list

  covint_bed:
    type: File
    outputSource: list2bed/output_file

steps:

  find_covered_intervals:
    run: ../../cwl_tools/gatk/FindCoveredIntervals.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_7)
      gatk:
        valueFrom: $(inputs.run_tools.gatk_path)

      tmp_dir: tmp_dir
      bams: bams
      patient_id: patient_id
      reference_sequence: reference_fasta
      min_base_quality: fci__minbq
      min_mapping_quality: fci__minmq
      coverage_threshold: fci__cov
      read_filters: fci__rf
      intervals: fci__intervals
      ignore_misencoded_base_qualities: fci__basq_fix
      out:
        valueFrom: ${return inputs.patient_id + ".fci.list"}
    out: [fci_list]

  list2bed:
    run: ../../cwl_tools/python/list2bed.cwl
    in:
      input_file: find_covered_intervals/fci_list
      output_filename:
        valueFrom: ${return inputs.input_file.basename.replace(".list", ".bed.srt")}
    out: [output_file]

  abra:
    run: ../../cwl_tools/abra/abra.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_7)
      abra:
        valueFrom: $(inputs.run_tools.abra_path)
      input_bams: bams
      targets: list2bed/output_file
      scratch_dir: abra__scratch
      patient_id: patient_id
      reference_fasta: reference_fasta
      kmer: abra__kmers
      mad: abra__mad
      threads:
        valueFrom: ${return 12}
      # Todo: Find a cleaner way
      working_directory:
        valueFrom: ${return inputs.scratch_dir + '__' + inputs.patient_id + '_' + Math.floor(Math.random() * 99999999);}
      out:
        valueFrom: |
          ${return inputs.input_bams.map(function(b){return b.basename.replace(".bam", "_IR.bam")})}
    out:
      [bams]

  parallel_fixmate:
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_7)
      fix_mate_information:
        valueFrom: $(inputs.run_tools.fx_path)
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
        java: string
        fix_mate_information: string
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
          run: ../../cwl_tools/picard/FixMateInformation.cwl
          in:
            java: java
            fix_mate_information: fix_mate_information
            input_bam: bam
            tmp_dir: tmp_dir
            sort_order: sort_order
            create_index: create_index
            compression_level: compression_level
            validation_stringency: validation_stringency
          out: [bam]
