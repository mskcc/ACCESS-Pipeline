name: Sample
type: record
fields:

  # Initial Files
  - name: fastq1
    type: File
  - name: fastq2
    type: File
  - name: sample_sheet
    type: File

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

  # Mapping
  - name: sam_file
    type: File?
  # ARRG
  - name: bam_file
    type: File?
  # MD
  - name: md_bamfile
    type: File?
  - name: md_metrics
    type: File?
  # FCI
  - name: covered_intervals_file
    type: File?
  # Abra
  - name: ir_bam
    type: File?
  # BQSR
  - name: bqsr_matrix
    type: File?
  - name: standard_bam_file
    type: File?

  # Collapsed Bams
  - name: unfiltered_bam_file
    type: File?
  - name: simplex_duplex_bam_file
    type: File?
  - name: duplex_bam_file
    type: File?

# Todo: add all manifest information to this struct