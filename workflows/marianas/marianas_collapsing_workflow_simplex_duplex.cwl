#!/usr/bin/env cwl-runner

cwlVersion: v1.0

# Todo: consider making Duplex and Simplex a single workflow
class: Workflow

requirements:
  InlineJavascriptRequirement: {}

inputs:

  input_bam: File
  reference_fasta: string
  reference_fasta_fai: string
  pileup: File
  mismatches: int
  wobble: int
  min_consensus_percent: int
  output_dir: string

outputs:

  output_fastq_1:
    type: File
    outputSource: rename_fastq_1/renamed_file

  output_fastq_2:
    type: File
    outputSource: rename_fastq_2/renamed_file

steps:

  first_pass:
    run: ../../cwl_tools/marianas/SimplexDuplexUMIBamToCollapsedFastqFirstPass.cwl
    in:
      input_bam: input_bam
      pileup: pileup
      wobble: wobble
      mismatches: mismatches
      min_consensus_percent: min_consensus_percent
      # todo: why doesn't secondaryFiles work?
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      output_dir: output_dir
    out:
      [first_pass_output_file, alt_allele_file, first_pass_output_dir]

  sort_by_mate_position:
    # todo - can use an existing sort cwl?
    run: ../../cwl_tools/marianas-sort/marianas-sort.cwl
    in:
      first_pass_file: first_pass/first_pass_output_file
    out:
      [output_file]

  second_pass:
    run: ../../cwl_tools/marianas/SimplexDuplexUMIBamToCollapsedFastqSecondPass.cwl
    in:
      input_bam: input_bam
      pileup: pileup
      wobble: wobble
      mismatches: mismatches
      min_consensus_percent: min_consensus_percent
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      first_pass_file: sort_by_mate_position/output_file
    out:
      [collapsed_fastq_1, collapsed_fastq_2]

  gzip_fastq_2:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: second_pass/collapsed_fastq_2
    out:
      [output]

  gzip_fastq_1:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: second_pass/collapsed_fastq_1
    out:
      [output]

  rename_fastq_1:
    run: ../../cwl_tools/innovation-rename-file/innovation-rename-file.cwl
    in:
      input_file: gzip_fastq_1/output
      new_name:
        source: input_bam
        valueFrom: $( self.basename.replace('.bam', '_R1_.fastq.gz') )
    out:
      [renamed_file]

  rename_fastq_2:
    run: ../../cwl_tools/innovation-rename-file/innovation-rename-file.cwl
    in:
      input_file: gzip_fastq_2/output
      new_name:
        source: input_bam
        valueFrom: $( self.basename.replace('.bam', '_R2_.fastq.gz') )
    out:
      [renamed_file]
