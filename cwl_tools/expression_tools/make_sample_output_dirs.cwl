#!toil-cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 2000

doc: |
  This tool groups files for one sample
  into a single directory

inputs:

  sample_id: string

  standard_bam:
    type: File
    secondaryFiles: [^.bai]
  unfiltered_bam:
    type: File
    secondaryFiles: [^.bai]
  simplex_bam:
    type: File
    secondaryFiles: [^.bai]
  duplex_bam:
    type: File
    secondaryFiles: [^.bai]

  r1_fastq: File
  r2_fastq: File
  first_pass_file: File
  first_pass_sorted: File
  first_pass_alt_alleles: File
  first_pass_insertions: File
  second_pass_insertions: File
  second_pass: File

outputs:

  directory: Directory

expression: |
  ${
    var output_files = [];

    output_files.push(inputs.standard_bam);
    output_files.push(inputs.unfiltered_bam);
    output_files.push(inputs.simplex_bam);
    output_files.push(inputs.duplex_bam);
    output_files.push(inputs.first_pass_insertions);
    output_files.push(inputs.second_pass_insertions);
    output_files.push(inputs.r1_fastq);
    output_files.push(inputs.r2_fastq);
    output_files.push(inputs.first_pass_file);
    output_files.push(inputs.first_pass_sorted);
    output_files.push(inputs.first_pass_alt_alleles);
    output_files.push(inputs.second_pass);

    return {
      'directory': {
        'class': 'Directory',
        'basename': inputs.sample_id,
        'listing': output_files
      }
    };
  }
