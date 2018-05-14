#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/schema_defs/Sample.cwl

inputs:

  tmp_dir: string

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
        waltz_path: string

  samples: ../resources/schema_defs/Sample.cwl#Sample[]

  title_file: File

  # Todo: Open a ticket
  # bwa cannot read symlink for the fasta.fai file?
  # so we need to use strings here instead of file types
  reference_fasta: string
  reference_fasta_fai: string

  # Marianas Clipping
  umi_length: int
  output_project_folder: string

  # Module 1
  md__assume_sorted: boolean
  md__compression_level: int
  md__create_index: boolean
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string

  # Module 2
  fci__minbq: int
  fci__minmq: int
  fci__cov: int
  fci__rf: string[]
  fci__intervals: string[]?
  abra__kmers: string
  abra__scratch: string
  abra__mad: int
  fix_mate_information__sort_order: string
  fix_mate_information__validation_stringency: string
  fix_mate_information__compression_level: int
  fix_mate_information__create_index: boolean
  bqsr__nct: int
  bqsr__knownSites_dbSNP: File
  bqsr__knownSites_millis: File
  bqsr__rf: string
  print_reads__nct: int
  print_reads__EOQ: boolean
  print_reads__baq: string

  # Marianas
  marianas__mismatches: int
  marianas__wobble: int
  marianas__min_mapping_quality: int
  marianas__min_base_quality: int
  marianas__min_consensus_percent: int

  # Waltz
  bed_file: File
  gene_list: File
  coverage_threshold: int
  waltz__min_mapping_quality: int

  # FindCoveredIntervals2
  fci_2__basq_fix: boolean?

outputs:

  output_samples:
    type:
      type: array
      items: ../resources/schema_defs/Sample.cwl#Sample
    outputSource: separate_bams/output_samples

  qc_pdf:
    type: File[]
    outputSource: qc_workflow/qc_pdf

steps:

  standard_bam_generation:
    run: ./standard_pipeline.cwl
    in:
      run_tools: run_tools
      samples: samples

      # Process Loop Umi Fastq
      umi_length: umi_length
      output_project_folder: output_project_folder
      # Module 1
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      md__create_index: md__create_index
      md__assume_sorted: md__assume_sorted
      md__compression_level: md__compression_level
      md__validation_stringency: md__validation_stringency
      md__duplicate_scoring_strategy: md__duplicate_scoring_strategy
      # Module 2
      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__cov: fci__cov
      fci__rf: fci__rf
      fci__intervals: fci__intervals
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      abra__mad: abra__mad
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__create_index: fix_mate_information__create_index
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      bqsr__nct: bqsr__nct
      bqsr__knownSites_dbSNP: bqsr__knownSites_dbSNP
      bqsr__knownSites_millis: bqsr__knownSites_millis
      bqsr__rf: bqsr__rf
      print_reads__nct: print_reads__nct
      print_reads__EOQ: print_reads__EOQ
      print_reads__baq: print_reads__baq
    out: [output_samples]

  waltz_standard:
    run: ./waltz/waltz-workflow.cwl
    in:
      run_tools: run_tools

      input_bam:
        source: standard_bam_generation/output_samples
        valueFrom: $(self.bamfile)

      bed_file: bed_file
      gene_list: gene_list
      coverage_threshold: coverage_threshold
      min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  ##############################
  # Match Normal pileups to    #
  # each Tumor and Normal bam  #
  ##############################

  match_normal_pileups:
    run: ../cwl_tools/expression_tools/match_normal_pileups.cwl
    in:
      samples: standard_bam_generation/output_samples
    out: [samples_with_matched_normal_pileups]

  umi_collapsing:
    run: ./marianas/marianas_collapsing_workflow.cwl
    in:
      run_tools: run_tools
      sample: match_normal_pileups/samples_with_matched_normal_pileups

      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      mismatches: marianas__mismatches
      wobble: marianas__wobble
      min_mapping_quality: marianas__min_mapping_quality
      min_base_quality: marianas__min_base_quality
      min_consensus_percent: marianas__min_consensus_percent
      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__cov: fci__cov
      fci__rf: fci__rf
      fci__intervals: fci__intervals
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      abra__mad: abra__mad
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__create_index: fix_mate_information__create_index
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency

    out: [output_samples]
    scatter: [sample]
    scatterMethod: dotproduct

  ############################
  # Group Bams by Patient ID #
  # and run Abra a 2nd time  #
  ############################

  group_samples_by_patient:
    run: ../cwl_tools/expression_tools/group_samples_by_patient.cwl
    in:
      samples: umi_collapsing/output_samples
    out:
      [grouped_samples]

  abra_workflow:
    run: ABRA/abra_workflow.cwl
    in:
      run_tools: run_tools
      reference_fasta: reference_fasta
      tmp_dir: tmp_dir

      samples: group_samples_by_patient/grouped_samples

      fci__minbq: fci__minbq
      fci__minmq: fci__minmq
      fci__rf: fci__rf
      fci__cov: fci__cov
      fci__intervals: fci__intervals
      fci__basq_fix: fci_2__basq_fix
      abra__mad: abra__mad
      abra__kmers: abra__kmers
      abra__scratch: abra__scratch
      fix_mate_information__sort_order: fix_mate_information__sort_order
      fix_mate_information__validation_stringency: fix_mate_information__validation_stringency
      fix_mate_information__compression_level: fix_mate_information__compression_level
      fix_mate_information__create_index: fix_mate_information__create_index
    out: [output_samples]
    scatter: [samples]
    scatterMethod: dotproduct

  ################################
  # Return to flat array of bams #
  ################################

  flatten_samples_array:
    run: ../cwl_tools/expression_tools/flatten_samples_array.cwl
    in:
      samples: abra_workflow/output_samples
    out: [output_samples]

  ################
  # SeparateBams #
  ################

  separate_bams:
    run: ../cwl_tools/marianas/SeparateBams.cwl
    in:
      run_tools: run_tools
      java_8:
        valueFrom: ${return inputs.run_tools.java_8}
      marianas_path:
        valueFrom: ${return inputs.run_tools.marianas_path}
      sample: flatten_samples_array/output_samples
      collapsed_bam:
        valueFrom: $(inputs.sample.unfiltered_bam)
    out: [output_samples]
    scatter: [sample]
    scatterMethod: dotproduct

  ######
  # QC #
  ######

  qc_workflow:
    run: ./QC/qc_workflow.cwl
    in:
      run_tools: run_tools
      title_file: title_file
      bed_file: bed_file
      gene_list: gene_list
      coverage_threshold: coverage_threshold
      waltz__min_mapping_quality: waltz__min_mapping_quality
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      samples: separate_bams/output_samples
      standard_bams:
        valueFrom: $( inputs.samples.map(function(x){return x.standard_bam)} )
      marianas_unfiltered_bams:
        valueFrom: $( inputs.samples.map(function(x){return x.unfiltered_bam)} )
      marianas_simplex_duplex_bams:
        valueFrom: $( inputs.samples.map(function(x){return x.simplex_duplex_bam)} )
      marianas_duplex_bams:
        valueFrom: $( inputs.samples.map(function(x){return x.duplex_bam)} )
    out:
      [qc_pdf]
