#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}


inputs:
  tmp_dir: string
  input_bam: File

  reference_fasta: string
  reference_fasta_fai: string

  # SortBam
  sort_order: string

  # GroupReads
  grouping_strategy: string
  min_mapping_quality: int
  tag_family_size_counts_output: string

  # CallDuplexConsensusReads
  call_duplex_min_reads: string

  # FilterConsensusReads: Simplex + Duplex + Singletons
  filter_min_base_quality: int

  # FilterConsensusReads: Simplex + Duplex
  filter_min_reads__simplex_duplex: string

  # FilterConsensusReads: Duplex
  filter_min_reads__duplex: string

  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string

outputs:

  simplex_duplex_singleton:
    type: File
    outputSource: fulcrum_postprocessing__simplex_duplex_singleton/bam

  simplex_duplex:
    type: File
    outputSource: fulcrum_postprocessing__simplex_duplex/bam

  duplex:
    type: File
    outputSource: fulcrum_postprocessing__duplex/bam

  duplex_seq_metrics:
    type: File
    outputSource: collect_duplex_seq_metrics/metrics

steps:

  innovation_extract_read_names:
    run: ../../cwl_tools/python/extract_read_names.cwl
    in:
      input_bam: input_bam
    out:
      [read_names]

  innovation_map_read_names_to_umis:
    run: ../../cwl_tools/python/map_read_names_to_umis.cwl
    in:
      read_names: innovation_extract_read_names/read_names
    out:
      [annotated_fastq]

  annotate_bam_with_umis:
    run: ../../cwl_tools/fulcrum/AnnotateBamWithUmis.cwl
    in:
      input_bam: input_bam
      annotated_fastq: innovation_map_read_names_to_umis/annotated_fastq
    out:
      [output_bam]

  sort_bam:
    run: ../../cwl_tools/fulcrum/SortBam.cwl
    in:
        input_bam: annotate_bam_with_umis/output_bam
        sort_order: sort_order
    out:
      [output_bam]

  set_mate_information:
    run: ../../cwl_tools/fulcrum/SetMateInformation.cwl
    in:
      input_bam: sort_bam/output_bam
    out:
      [output_bam]

  group_reads_by_umi:
    run: ../../cwl_tools/fulcrum/GroupReadsByUmi.cwl
    in:
      strategy: grouping_strategy
      min_mapping_quality: min_mapping_quality
      tag_family_size_counts_output: tag_family_size_counts_output
      input_bam: set_mate_information/output_bam
    out:
      [output_bam]

  collect_duplex_seq_metrics:
    run: ../../cwl_tools/fulcrum/CollectDuplexSeqMetrics.cwl
    in:
      input_bam: group_reads_by_umi/output_bam
    out:
      [metrics]

  #####################################
  # Actual Collapsing Steps           #
  # Here we generate 3 different bams #
  #####################################

  call_duplex_consensus_reads:
    run: ../../cwl_tools/fulcrum/CallDuplexConsensusReads.cwl
    in:
      input_bam: group_reads_by_umi/output_bam
      call_duplex_min_reads: call_duplex_min_reads
    out:
      [output_bam]

  # To obtain Simplex + Duplex + Singleton bam,
  # with Base Quality > 30
  filter_consensus_reads__simplex_duplex_singleton:
    run: ../../cwl_tools/fulcrum/FilterConsensusReads.cwl
    in:
      input_bam: call_duplex_consensus_reads/output_bam
      reference_fasta: reference_fasta
      min_reads: call_duplex_min_reads
      min_base_quality: filter_min_base_quality
    out:
      [output_bam]

  # To obtain Simplex + Duplex bam
  filter_consensus_reads__simplex_duplex:
    run: ../../cwl_tools/fulcrum/FilterConsensusReads.cwl
    in:
      input_bam: filter_consensus_reads__simplex_duplex_singleton/output_bam
      reference_fasta: reference_fasta
      min_reads: filter_min_reads__simplex_duplex
      min_base_quality: filter_min_base_quality
    out:
      [output_bam]

  # To obtain Duplex bam
  filter_consensus_reads__duplex:
    run: ../../cwl_tools/fulcrum/FilterConsensusReads.cwl
    in:
      input_bam: filter_consensus_reads__simplex_duplex/output_bam
      reference_fasta: reference_fasta
      min_reads: filter_min_reads__duplex
      min_base_quality: filter_min_base_quality
    out:
      [output_bam]

  ##########################
  # Fulcrum Postprocessing #
  ##########################

  fulcrum_postprocessing__simplex_duplex_singleton:
    run: ./fulcrum_postprocessing.cwl
    in:
      input_bam: filter_consensus_reads__simplex_duplex_singleton/output_bam

      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix:
        valueFrom: ${ return '_fulcrumSimplexDuplexSingleton' }
    out:
      [bam]

  fulcrum_postprocessing__simplex_duplex:
    run: ./fulcrum_postprocessing.cwl
    in:
      input_bam: filter_consensus_reads__simplex_duplex/output_bam

      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix:
        valueFrom: ${ return '_fulcrumSimplexDuplex' }
    out:
      [bam]

  fulcrum_postprocessing__duplex:
    run: ./fulcrum_postprocessing.cwl
    in:
      input_bam: filter_consensus_reads__duplex/output_bam

      tmp_dir: tmp_dir
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      output_suffix:
        valueFrom: ${ return '_fulcrumDuplex' }
    out:
      [bam]
