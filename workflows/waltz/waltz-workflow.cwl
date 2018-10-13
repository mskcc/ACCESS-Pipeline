cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_tools/schemas.yaml
      - $import: ../../resources/run_params/schemas/waltz.yaml

inputs:
  run_tools: ../../resources/run_tools/schemas.yaml#run_tools
  waltz__params: ../../resources/run_params/schemas/waltz.yaml#waltz__params

  input_bam:
    type: File
    secondaryFiles: [^.bai]
  gene_list: File
  bed_file: File
  reference_fasta: string
  reference_fasta_fai: string

outputs:
  pileup:
    type: File
    outputSource: pileup_metrics/pileup

  waltz_output_files:
    type: File[]
    outputSource: grouped_waltz_files/waltz_files

steps:

  count_reads:
    run: ../../cwl_tools/waltz/CountReads.cwl
    in:
      run_tools: run_tools
      params: waltz__params
      java_8:
        valueFrom: $(inputs.run_tools.java_8)
      waltz_path:
        valueFrom: $(inputs.run_tools.waltz_path)
      coverage_threshold:
        valueFrom: $(inputs.params.coverage_threshold)

      input_bam: input_bam
      gene_list: gene_list
      bed_file: bed_file
    out: [
      covered_regions,
      fragment_sizes,
      read_counts
    ]

  pileup_metrics:
    run: ../../cwl_tools/waltz/PileupMetrics.cwl
    in:
      run_tools: run_tools
      params: waltz__params
      java_8:
        valueFrom: $(inputs.run_tools.java_8)
      waltz_path:
        valueFrom: $(inputs.run_tools.waltz_path)
      min_mapping_quality:
        valueFrom: $(inputs.params.min_mapping_quality)

      input_bam: input_bam
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      bed_file: bed_file
    out: [
      pileup,
      pileup_without_duplicates,
      intervals,
      intervals_without_duplicates
    ]

  grouped_waltz_files:
    run: ../../cwl_tools/expression_tools/group_waltz_files.cwl
    in:
      covered_regions: count_reads/covered_regions
      fragment_sizes: count_reads/fragment_sizes
      read_counts: count_reads/read_counts
      pileup: pileup_metrics/pileup
      pileup_without_duplicates: pileup_metrics/pileup_without_duplicates
      intervals: pileup_metrics/intervals
      intervals_without_duplicates: pileup_metrics/intervals_without_duplicates
    out: [waltz_files]
