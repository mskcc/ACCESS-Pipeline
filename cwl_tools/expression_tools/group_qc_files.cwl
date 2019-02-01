#!toil-cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 2000

doc: |
  This tool groups waltz qc files into a single directory

inputs:

  standard_pool_a: Directory
  unfiltered_pool_a: Directory
  simplex_pool_a: Directory
  duplex_pool_a: Directory
  standard_pool_b: Directory
  unfiltered_pool_b: Directory
  simplex_pool_b: Directory
  duplex_pool_b: Directory

  all_fp_results: Directory
  gender_table: File
  family_sizes: File
  family_types_A: File
  family_types_B: File
  combined_qc: File

outputs:

  qc_files: Directory

expression: |
  ${
    var output_files = [];

    output_files.push(inputs.standard_pool_a);
    output_files.push(inputs.unfiltered_pool_a);
    output_files.push(inputs.simplex_pool_a);
    output_files.push(inputs.duplex_pool_a);
    output_files.push(inputs.standard_pool_b);
    output_files.push(inputs.unfiltered_pool_b);
    output_files.push(inputs.simplex_pool_b);
    output_files.push(inputs.duplex_pool_b);

    output_files.push(inputs.all_fp_results);
    output_files.push(inputs.gender_table);

    output_files.push(inputs.family_sizes);
    output_files.push(inputs.family_types_A);
    output_files.push(inputs.family_types_B);
    output_files.push(inputs.combined_qc);

    return {
      'qc_files': {
        'class': 'Directory',
        'basename': 'QC_Results',
        'listing': output_files
      }
    };
  }
