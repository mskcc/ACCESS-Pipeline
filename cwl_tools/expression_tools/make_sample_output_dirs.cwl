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

  processed_fastq_1: File
  processed_fastq_2: File
  info: File
  sample_sheets: File
  umi_frequencies: File
  composite_umi_frequencies: File
  clstats1: File
  clstats2: File
#  covint_list: File
#  covint_bed: File

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
    output_files.push(inputs.processed_fastq_1);
    output_files.push(inputs.processed_fastq_2);
    output_files.push(inputs.info);
    output_files.push(inputs.sample_sheets);
    output_files.push(inputs.umi_frequencies);
    output_files.push(inputs.composite_umi_frequencies);
    output_files.push(inputs.clstats1);
    output_files.push(inputs.clstats2);

    return {
      'directory': {
        'class': 'Directory',
        'basename': 'Sample_' + inputs.standard_bam.basename.split('IGO')[0].split('_cl')[0],
        'listing': output_files
      }
    };
  }