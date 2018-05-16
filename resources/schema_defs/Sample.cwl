# Sample Schema
#
# This data structure holds all relevant info for a Sample
# Any bams, fastqs, sample sheets, stats files, metadata, or
# other sample-related information is stored here, and accessed by
# the tools by referencing the relevant fields from this struct.

name: Sample
type: record
fields:

  # Initial Files
  - name: fastq1
    type: File
  - name: fastq2
    type: File
  - name: sample_sheet
    type: File?

  # Sample Metadata
  - name: patient_id
    type: string
  - name: sample_class
    type: string
#    symbols: [Tumor, Normal]

  - name: adapter
    type: string
  - name: adapter2
    type: string

  - name: add_rg_ID
    type: string
  - name: add_rg_PU
    type: string
  - name: add_rg_SM
    type: string
  - name: add_rg_PL
    type: string
  - name: add_rg_CN
    type: string
  - name: add_rg_LB
    type: int

  # UMI Clipping
  - name: clipped_fastq_1
    type: File?
  - name: clipped_fastq_2
    type: File?
  - name: composite_umi_frequencies
    type: File?
  - name: info
    type: File?
  - name: umi_frequencies
    type: File?

  # Trimming
  - name: clfastq1
    type: File?
  - name: clfastq2
    type: File?
  - name: clstats1
    type: File?
  - name: clstats2
    type: File?

  # BWA mem 1
  - name: sam_1
    type: File?
  # ARRG 1
  - name: rg_bam_1
    type: File?
  - name: rg_bai_1
    type: File?
  # MD
  - name: md_bam
    type: File?
  - name: md_bai
    type: File?
  - name: md_metrics
    type: File?
  # FCI 1
  - name: covered_intervals_file_1
    type: File?
  # Abra 1
  - name: ir_bam_1
    type: File?
  # FX 1
  - name: fx_bam_1
    type: File?
  - name: fx_bai_1
    type: File?
  # BQSR
  - name: bqsr_matrix
    type: File?
  - name: standard_bam
    type: File?

  # Standard Waltz Metrics (needed for normal_pileup)
#  - name: standard_waltz_metrics
#    type: Directory

  # Collapsed Bams
  - name: unfiltered_bam_file
    type: File?
  - name: simplex_duplex_bam_file
    type: File?
  - name: duplex_bam_file
    type: File?

  # BWA mem 2
  - name: sam_2
    type: File?
  # ARRG 2
  - name: rg_bam_2
    type: File?
  - name: rg_bai_2
    type: File?
  # FCI 2
  - name: covered_intervals_file_2
    type: File?
  # Abra 2
  - name: ir_bam_2
    type: File?
  # FX 2
  - name: fx_bam_2
    type: File?
  - name: fx_bai_2
    type: File?

# Todo: add all manifest information to this struct