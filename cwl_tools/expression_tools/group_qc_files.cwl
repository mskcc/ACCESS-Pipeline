#!toil-cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  - class: InlineJavascriptRequirement

doc: |
  This tool groups qc files into a single directory

inputs:

  standard_aggregate_bam_metrics_pool_a: Directory
  unfiltered_aggregate_bam_metrics_pool_a: Directory
  simplex_duplex_aggregate_bam_metrics_pool_a: Directory
  duplex_aggregate_bam_metrics_pool_a: Directory
  standard_aggregate_bam_metrics_pool_b: Directory
  unfiltered_aggregate_bam_metrics_pool_b: Directory
  simplex_duplex_aggregate_bam_metrics_pool_b: Directory
  duplex_aggregate_bam_metrics_pool_b: Directory

  all_fp_results: Directory
  gender_table: File
  noise_alt_percent: File
  noise_contributing_sites: File
  family_sizes: File
  family_types_A: File
  family_types_B: File
  combined_qc: File

outputs:

  qc_files: Directory

expression: |
  ${
    var output_files = [];

    output_files.push(inputs.standard_aggregate_bam_metrics_pool_a);
    output_files.push(inputs.unfiltered_aggregate_bam_metrics_pool_a);
    output_files.push(inputs.simplex_duplex_aggregate_bam_metrics_pool_a);
    output_files.push(inputs.duplex_aggregate_bam_metrics_pool_a);
    output_files.push(inputs.standard_aggregate_bam_metrics_pool_b);
    output_files.push(inputs.unfiltered_aggregate_bam_metrics_pool_b);
    output_files.push(inputs.simplex_duplex_aggregate_bam_metrics_pool_b);
    output_files.push(inputs.duplex_aggregate_bam_metrics_pool_b);
    output_files.push(inputs.all_fp_results);
    output_files.push(inputs.gender_table);
    output_files.push(inputs.noise_alt_percent);
    output_files.push(inputs.noise_contributing_sites);
    output_files.push(inputs.family_sizes);
    output_files.push(inputs.family_types_A);
    output_files.push(inputs.family_types_B);
    output_files.push(inputs.combined_qc);

    return {
      'directory': {
        'class': 'Directory',
        'basename': 'QC_Results',
        'listing': output_files
      }
    };
  }