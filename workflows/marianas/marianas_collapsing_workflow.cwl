cwlVersion: v1.0

class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/collapsing_tools.yaml
      - $import: ../../resources/schemas/params/marianas_collapsing.yaml
      - $import: ../../resources/schemas/params/add_or_replace_read_groups.yaml

inputs:
  run_tools: ../../resources/schemas/collapsing_tools.yaml#run_tools

  marianas_collapsing__params: ../../resources/schemas/params/marianas_collapsing.yaml#marianas_collapsing__params
  add_or_replace_read_groups__params: ../../resources/schemas/params/add_or_replace_read_groups.yaml#add_or_replace_read_groups__params

  input_bam: File
  reference_fasta: string
  reference_fasta_fai: string
  pileup: File

  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string

outputs:

  collapsed_bams:
    type: File
    outputSource: post_collapsing_realignment/bam

  first_pass_output_file:
    type: File
    outputSource: first_pass/first_pass_output_file

  first_pass_alt_allele:
    type: File
    outputSource: first_pass/alt_allele_file

  first_pass_insertions:
    type: File
    outputSource: first_pass/first_pass_insertions

  first_pass_alt_allele_sorted:
    type: File
    outputSource: sort_by_mate_position/output_file

  collapsed_fastq_1:
    type: File
    outputSource: gzip_fastq_1/output

  collapsed_fastq_2:
    type: File
    outputSource: gzip_fastq_2/output

  second_pass_alt_alleles:
    type: File
    outputSource: second_pass/second_pass_alt_alleles

  second_pass_insertions:
    type: File
    outputSource: second_pass/second_pass_insertions

steps:

  first_pass:
    run: ../../cwl_tools/marianas/UMIBamToCollapsedFastqFirstPass.cwl
    in:
      run_tools: run_tools
      params: marianas_collapsing__params
      java_8:
        valueFrom: ${return inputs.run_tools.java_8}
      marianas_path:
        valueFrom: ${return inputs.run_tools.marianas_path}
      input_bam: input_bam
      pileup: pileup

      wobble:
        valueFrom: $(inputs.params.wobble)
      mismatches:
        valueFrom: $(inputs.params.mismatches)
      min_mapping_quality:
        valueFrom: $(inputs.params.min_mapping_quality)
      min_base_quality:
        valueFrom: $(inputs.params.min_base_quality)
      min_consensus_percent:
        valueFrom: $(inputs.params.min_consensus_percent)

      # todo: why doesn't secondaryFiles work?
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
    out:
      [first_pass_output_file, first_pass_insertions, alt_allele_file, first_pass_output_dir]

  sort_by_mate_position:
    # todo - can use an existing sort cwl?
    run: ../../cwl_tools/marianas-sort/marianas-sort.cwl
    in:
      first_pass_file: first_pass/first_pass_output_file
    out:
      [output_file]

  second_pass:
    run: ../../cwl_tools/marianas/UMIBamToCollapsedFastqSecondPass.cwl
    in:
      run_tools: run_tools
      params: marianas_collapsing__params
      java_8:
        valueFrom: ${return inputs.run_tools.java_8}
      marianas_path:
        valueFrom: ${return inputs.run_tools.marianas_path}
      input_bam: input_bam
      pileup: pileup
      first_pass_file: sort_by_mate_position/output_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai

      wobble:
        valueFrom: $(inputs.params.wobble)
      mismatches:
        valueFrom: $(inputs.params.mismatches)
      min_mapping_quality:
        valueFrom: $(inputs.params.min_mapping_quality)
      min_base_quality:
        valueFrom: $(inputs.params.min_base_quality)
      min_consensus_percent:
        valueFrom: $(inputs.params.min_consensus_percent)
    out:
      [collapsed_fastq_1, collapsed_fastq_2, second_pass_alt_alleles, second_pass_insertions]

  gzip_fastq_1:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: second_pass/collapsed_fastq_1
    out:
      [output]

  gzip_fastq_2:
    run: ../../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
    in:
      input_fastq: second_pass/collapsed_fastq_2
    out:
      [output]

  rename_fastq_1:
    run: ../../cwl_tools/innovation-rename-file/innovation-rename-file.cwl
    in:
      input_file: gzip_fastq_1/output
      new_name:
        source: input_bam
        valueFrom: $(self.basename.replace('.bam', '_R1_.fastq.gz'))
    out:
      [renamed_file]

  rename_fastq_2:
    run: ../../cwl_tools/innovation-rename-file/innovation-rename-file.cwl
    in:
      input_file: gzip_fastq_2/output
      new_name:
        source: input_bam
        valueFrom: $(self.basename.replace('.bam', '_R2_.fastq.gz'))
    out:
      [renamed_file]

  post_collapsing_realignment:
    run: ./collapsed_fastq_to_bam.cwl
    in:
      run_tools: run_tools
      add_or_replace_read_groups__params: add_or_replace_read_groups__params
      fastq1: rename_fastq_1/renamed_file
      fastq2: rename_fastq_2/renamed_file
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
    out: [bam, bai]
