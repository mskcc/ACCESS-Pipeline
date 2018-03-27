cwlVersion: v1.0

class: Workflow

doc: |
  This workflow is useful for creating pairs of smaller fastqs that
  come from paired input fastqs.
  They can be subsetted to a specific region in the genome,
  and may also be optionally filtered to only paired and mapped reads.

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  fastq_1: File[]
  fastq_2: File[]
  sample_sheet: File[]

  umi_length: int
  output_project_folder: string

  reference_fasta: string
  reference_fasta_fai: string

  # Module 1
  tmp_dir: string
  adapter: string[]
  adapter2: string[]
  add_rg_PL: string
  add_rg_CN: string
  add_rg_LB: int[]
  add_rg_ID: string[]
  add_rg_PU: string[]
  add_rg_SM: string[]

  md__assume_sorted: boolean
  md__compression_level: int
  md__create_index: boolean
  md__validation_stringency: string
  md__duplicate_scoring_strategy: string

  # bed file with regions to extract from
  subset_region: string
  paired_only: boolean
  mapped_only: boolean

outputs:
  test_fastq_1:
    type: File[]
    outputSource: scatter/test_fastq_1

  test_fastq_2:
    type: File[]
    outputSource: scatter/test_fastq_2

steps:

  # Todo: Is there a way to have scatter as a top level key instead of this subworkflow?
  scatter:
    scatter: [
      fastq_1,
      fastq_2,
      sample_sheet,
      add_rg_LB,
      add_rg_ID,
      add_rg_PU,
      add_rg_SM,
      adapter,
      adapter2
    ]
    scatterMethod: dotproduct

    in:
      fastq_1: fastq_1
      fastq_2: fastq_2
      sample_sheet: sample_sheet
      umi_length: umi_length
      output_project_folder: output_project_folder
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      tmp_dir: tmp_dir
      adapter: adapter
      adapter2: adapter2
      add_rg_PL: add_rg_PL
      add_rg_CN: add_rg_CN
      add_rg_LB: add_rg_LB
      add_rg_ID: add_rg_ID
      add_rg_PU: add_rg_PU
      add_rg_SM: add_rg_SM
      md__assume_sorted: md__assume_sorted
      md__compression_level: md__compression_level
      md__create_index: md__create_index
      md__validation_stringency: md__validation_stringency
      md__duplicate_scoring_strategy: md__duplicate_scoring_strategy
      subset_region: subset_region
      paired_only: paired_only
      mapped_only: mapped_only

    out: [test_fastq_1, test_fastq_2]

    run:
      class: Workflow
      inputs:
        fastq_1: File
        fastq_2: File
        sample_sheet: File
        umi_length: int
        output_project_folder: string
        reference_fasta: string
        reference_fasta_fai: string
        tmp_dir: string
        adapter: string
        adapter2: string
        add_rg_PL: string
        add_rg_CN: string
        add_rg_LB: int
        add_rg_ID: string
        add_rg_PU: string
        add_rg_SM: string
        md__assume_sorted: boolean
        md__compression_level: int
        md__create_index: boolean
        md__validation_stringency: string
        md__duplicate_scoring_strategy: string
        subset_region: string
        paired_only: boolean
        mapped_only: boolean

      outputs:
        test_fastq_1:
          type: File
          outputSource: gzip_1/output

        test_fastq_2:
          type: File
          outputSource: gzip_2/output

      steps:

        umi_clipping:
          run: ../cwl_tools/marianas/ProcessLoopUMIFastq.cwl
          in:
            fastq1: fastq_1
            fastq2: fastq_2
            sample_sheet: sample_sheet
            umi_length: umi_length
            output_project_folder: output_project_folder
          out: [processed_fastq_1, processed_fastq_2]

        module_1:
          run: ./module-1.cwl
          in:
            tmp_dir: tmp_dir
            fastq1: umi_clipping/processed_fastq_1
            fastq2: umi_clipping/processed_fastq_2
            adapter: adapter
            adapter2: adapter2
            reference_fasta: reference_fasta
            reference_fasta_fai: reference_fasta_fai

            add_rg_LB: add_rg_LB
            add_rg_PL: add_rg_PL
            add_rg_ID: add_rg_ID
            add_rg_PU: add_rg_PU
            add_rg_SM: add_rg_SM
            add_rg_CN: add_rg_CN

            md__assume_sorted: md__assume_sorted
            md__compression_level: md__compression_level
            md__create_index: md__create_index
            md__validation_stringency: md__validation_stringency
            md__duplicate_scoring_strategy: md__duplicate_scoring_strategy

            output_suffix:
              valueFrom: ${ return '_standard' }
          out: [bam, bai, md_metrics]

        sort_bam:
          run: ../cwl_tools/samtools/sort-by-coordinate.cwl
          in:
            bam: module_1/bam
          out: [output_bam]

        index_bam:
          run: ../cwl_tools/samtools/index.cwl
          in:
            input: sort_bam/output_bam
          out: [bam_with_bai]

        extract_region:
          run: ../cwl_tools/samtools/view.cwl
          in:
            bam: index_bam/bam_with_bai
            region: subset_region
            mapped_only: mapped_only
            paired_only: paired_only
          out:
            [output_bam]

        sort_queryname:
          run: ../cwl_tools/samtools/sort-by-queryname.cwl
          in:
            bam: extract_region/output_bam
          out: [output_bam]

        convert_to_fastq:
          run: ../cwl_tools/samtools/fastq.cwl
          in:
            input_bam: sort_queryname/output_bam
            fastq_1_name:
              valueFrom: ${ return self.inputs.bam.basename.replace('.bam', '_R1.fastq')
            fastq_2_name:
              valueFrom: ${ return self.inputs.bam.basename.replace('.bam', '_R2.fastq')
          out: [output_read_1, output_read_2]

        reverse_umis:
          run: ../cwl_tools/python/reverse_clip.cwl
          in:
            fastq_1: convert_to_fastq/output_read_1
            fastq_2: convert_to_fastq/output_read_2
          out: [reversed_fastq_1, reversed_fastq_2]

        gzip_1:
          run: ../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
          in:
            input_fastq: reverse_umis/reversed_fastq_1
          out:
            [output]

        gzip_2:
          run: ../cwl_tools/innovation-gzip-fastq/innovation-gzip-fastq.cwl
          in:
            input_fastq: reverse_umis/reversed_fastq_2
          out:
            [output]
