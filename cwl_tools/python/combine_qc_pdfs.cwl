cwlVersion: v1.0

class: CommandLineTool

baseCommand: [combine_qc_pdfs]

inputs:

  project_name:
    type: string
    inputBinding:
      prefix: -p

  title_page:
    type: File
    inputBinding:
      position: 1

  read_counts:
    type: File
    inputBinding:
      position: 2

  align_rate:
    type: File
    inputBinding:
      position: 3

  on_target_rate:
    type: File
    inputBinding:
      position: 4

  gc_cov_each_sample:
    type: File
    inputBinding:
      position: 5

  insert_sizes:
    type: File
    inputBinding:
      position: 6

  coverage_per_interval:
    type: File
    inputBinding:
      position: 7

  cov_and_family_type_A:
    type: File
    inputBinding:
      position: 8

  average_coverage_exon_level_A:
    type: File
    inputBinding:
      position: 9

  cov_and_family_type_B:
    type: File
    inputBinding:
      position: 10

  base_quality_plot:
    type: File
    inputBinding:
      position: 11

  family_sizes_all:
    type: File
    inputBinding:
      position: 12

  family_sizes_simplex:
    type: File
    inputBinding:
      position: 13

  family_sizes_duplex:
    type: File
    inputBinding:
      position: 14

  noise_alt_percent:
    type: File
    inputBinding:
      position: 15

  noise_by_substitution:
    type: File
    inputBinding:
      position: 16

  noise_contributing_sites:
    type: File
    inputBinding:
      position: 17

  fingerprinting_qc:
    type: File
    inputBinding:
      position: 18

  gender_check:
    type: File
    inputBinding:
      position: 19

  pipeline_inputs:
    type: File
    inputBinding:
      position: 20

outputs:

  combined_qc:
    type: File
    outputBinding:
      glob: '*.pdf'
