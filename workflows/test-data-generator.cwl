cwlVersion: v1.0

class: Workflow

inputs:
  fastq_1: File
  fastq_2: File
  sample_sheet: File

  add_rg_LB: string
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string
  tmp_dir: string

  # bed file with regions to extract from
  subset_region: string

outputs:

  test_fastq_1: gzip/fastq_1
  test_fastq_2: gzip/fastq_2

steps:

  process_loop_umi_fastq:
    run: ../tools/marianas/ProcessLoopUMIFastq.cwl

    in:
      fastq_1: fastq_1
      fastq_2: fastq_2
      sample_sheet: sample_sheet

    out: [clipped_fastq_1, clipped_fastq_2]

  module_1:
    run: ./module-1.cwl

    in:
      fastq1: process_loop_umi_fastq/clipped_fastq_1
      fastq2: process_loop_umi_fastq/clipped_fastq_2

      adapter: adapter
      adapter2: adapter2

      reference_fasta: string
      reference_fasta_fai: string

      add_rg_LB: add_rg_LB
      add_rg_PL: add_rg_PL

      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU

      add_rg_SM: add_rg_SM
      add_rg_CN: add_rg_CN
      tmp_dir: tmp_dir
      output_suffix: output_suffix

    out: [bam]

  sort_bam:
    run: ../tools/samtools/sort-by-coordinate.cwl
    in: module_1/bam
    out: [bam]

  index_bam:
    run: ../tools/samtools/index.cwl
    in: sort_bam/bam
    out: [bam]

  extract_bed_region_mapped_paired:
    run: ../tools/samtools/view.cwl
    in:
      bam: index_bam/bam
      region: subset_region

      mapped: true
      paired: true
    out:
      [bam]

  sort_queryname:
    run: ../tools/samtools/sort-by-queryname.cwl
    in:
      bam: extract_bed_region_mapped_paired/bam
    out: [bam]

  convert_to_fastq:
    run: ../tools/samtools/fastq.cwl
    in:
      bam: sort_queryname/bam
      fastq_1_name:
        valueFrom: ${ return self.inputs.bam.basename.replace('.bam', '_R1.fastq')
      fastq_2_name:
        valueFrom: ${ return self.inputs.bam.basename.replace('.bam', '_R2.fastq')
    out: [fastq_1, fastq_2]

  reverse_umis:
    run: ../tools/reverse-clip.cwl
    in:
      fastq_1: convert_to_fastq/fastq_1
      fastq_2: convert_to_fastq/fastq_2
    out: [fastq_1, fastq_2]

  gzip:
    run: ../tools/innovation-gzip-fastq.cwl
    in:
      fastq_1: reverse_umis/fastq_1
      fastq_2: reverse_umis/fastq_2
    out: [fastq_1, fastq_2]
