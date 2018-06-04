#!toil-cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  - class: InlineJavascriptRequirement

doc: |
  This tool groups files for one sample
  into a single directory

inputs:

  standard_bam:
    type: File
    secondaryFiles: [^.bai]
  unfiltered_bam:
    type: File
    secondaryFiles: [^.bai]
  simplex_duplex_bam:
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
  second_pass: File

outputs:

  directory:
    type: Directory

# Todo: Sample Name in basename
# 'basename': inputs.standard_bam.basename.split('IGO')[0],
expression: |
  ${
    var output_files = [];

    output_files.push(inputs.standard_bam);
    output_files.push(inputs.unfiltered_bam);
    output_files.push(inputs.simplex_duplex_bam);
    output_files.push(inputs.duplex_bam);
    output_files.push(inputs.r1_fastq);
    output_files.push(inputs.r2_fastq);
    output_files.push(inputs.first_pass_file);
    output_files.push(inputs.first_pass_sorted);
    output_files.push(inputs.first_pass_alt_alleles);
    output_files.push(inputs.second_pass);

    return {
      'directory': {
        'class': 'Directory',
        'basename': 'Sample_' + inputs.standard_bam.basename.split('IGO')[0],
        'listing': output_files
      }
    };
  }