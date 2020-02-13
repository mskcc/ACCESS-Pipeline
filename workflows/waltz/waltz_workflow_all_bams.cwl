cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/collapsing_tools.yaml
      - $import: ../../resources/schemas/params/waltz.yaml

inputs:
  run_tools: ../../resources/schemas/collapsing_tools.yaml#run_tools
  waltz__params: ../../resources/schemas/params/waltz.yaml#waltz__params

  title_file: File
  pool_a_bed_file: File
  pool_b_bed_file: File
  pool_a_bed_file_exonlevel: File
  gene_list: File
  reference_fasta: string
  reference_fasta_fai: string

  standard_bams: File[]
  marianas_unfiltered_bams: File[]
  marianas_simplex_bams: File[]
  marianas_duplex_bams: File[]

outputs:

  waltz_standard_pool_a_files:
    type: Directory
    outputSource: standard_pool_a_consolidate_bam_metrics/directory

  waltz_unfiltered_pool_a_files:
    type: Directory
    outputSource: unfiltered_pool_a_consolidate_bam_metrics/directory

  waltz_simplex_pool_a_files:
    type: Directory
    outputSource: simplex_pool_a_consolidate_bam_metrics/directory

  waltz_duplex_pool_a_files:
    type: Directory
    outputSource: duplex_pool_a_consolidate_bam_metrics/directory

  waltz_standard_pool_b_files:
    type: Directory
    outputSource: standard_pool_b_consolidate_bam_metrics/directory

  waltz_unfiltered_pool_b_files:
    type: Directory
    outputSource: unfiltered_pool_b_consolidate_bam_metrics/directory

  waltz_simplex_pool_b_files:
    type: Directory
    outputSource: simplex_pool_b_consolidate_bam_metrics/directory

  waltz_duplex_pool_b_files:
    type: Directory
    outputSource: duplex_pool_b_consolidate_bam_metrics/directory

  waltz_standard_a_exon_level_files:
    type: Directory
    outputSource: waltz_standard_a_exon_level_consolidate_bam_metrics/directory

  waltz_unfiltered_a_exon_level_files:
    type: Directory
    outputSource: waltz_unfiltered_a_exon_level_consolidate_bam_metrics/directory

  waltz_simplex_a_exon_level_files:
    type: Directory
    outputSource: waltz_simplex_a_exon_level_consolidate_bam_metrics/directory

  waltz_duplex_a_exon_level_files:
    type: Directory
    outputSource: waltz_duplex_a_exon_level_consolidate_bam_metrics/directory

  waltz_unfiltered_pool_a_pileups:
    type: File[]
    outputSource: waltz_unfiltered_pool_a/pileup

  waltz_duplex_pool_a_pileups:
    type: File[]
    outputSource: waltz_duplex_pool_a/pileup

steps:

  ################
  # Run Waltz 9x #
  ################

  waltz_standard_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: standard_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  waltz_unfiltered_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_unfiltered_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_simplex_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_simplex_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_duplex_pool_a:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_duplex_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_standard_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: standard_bams
      gene_list: gene_list
      bed_file: pool_b_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: [input_bam]
    scatterMethod: dotproduct

  waltz_unfiltered_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_unfiltered_bams
      gene_list: gene_list
      bed_file: pool_b_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_simplex_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_simplex_bams
      gene_list: gene_list
      bed_file: pool_b_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_duplex_pool_b:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_duplex_bams
      gene_list: gene_list
      bed_file: pool_b_bed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  #########################################
  # Additional Waltz Run for DMP bedfiles #
  #########################################

  waltz_standard_a_exon_level:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: standard_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file_exonlevel
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_unfiltered_a_exon_level:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_unfiltered_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file_exonlevel
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_simplex_a_exon_level:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_simplex_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file_exonlevel
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct

  waltz_duplex_a_exon_level:
    run: ./waltz-workflow.cwl
    in:
      run_tools: run_tools
      waltz__params: waltz__params
      input_bam: marianas_duplex_bams
      gene_list: gene_list
      bed_file: pool_a_bed_file_exonlevel
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out: [pileup, waltz_output_files]
    scatter: input_bam
    scatterMethod: dotproduct


  ############################
  # Group waltz output files #
  ############################

  standard_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_standard_a')
      files: waltz_standard_pool_a/waltz_output_files
    out:
      [directory]

  unfiltered_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_unfiltered_a')
      files: waltz_unfiltered_pool_a/waltz_output_files
    out:
      [directory]

  simplex_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_simplex_a')
      files: waltz_simplex_pool_a/waltz_output_files
    out:
      [directory]

  duplex_pool_a_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_duplex_a')
      files: waltz_duplex_pool_a/waltz_output_files
    out:
      [directory]

  standard_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_standard_b')
      files: waltz_standard_pool_b/waltz_output_files
    out:
      [directory]

  unfiltered_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_unfiltered_b')
      files: waltz_unfiltered_pool_b/waltz_output_files
    out:
      [directory]

  simplex_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_simplex_b')
      files: waltz_simplex_pool_b/waltz_output_files
    out:
      [directory]

  duplex_pool_b_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_duplex_b')
      files: waltz_duplex_pool_b/waltz_output_files
    out:
      [directory]

  waltz_standard_a_exon_level_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_standard_a_exon_level')
      files: waltz_standard_a_exon_level/waltz_output_files
    out:
      [directory]

  waltz_unfiltered_a_exon_level_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_unfiltered_a_exon_level')
      files: waltz_unfiltered_a_exon_level/waltz_output_files
    out:
      [directory]

  waltz_simplex_a_exon_level_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_simplex_a_exon_level')
      files: waltz_simplex_a_exon_level/waltz_output_files
    out:
      [directory]

  waltz_duplex_a_exon_level_consolidate_bam_metrics:
    run: ../../cwl_tools/expression_tools/consolidate_files.cwl
    in:
      output_directory_name:
        valueFrom: $('waltz_duplex_a_exon_level')
      files: waltz_duplex_a_exon_level/waltz_output_files
    out:
      [directory]
