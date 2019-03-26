cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1

baseCommand: plots_module.r

inputs:

  title_file:
    type: File
    inputBinding:
      prefix: --title_file_path

  tables:
    type: Directory
    inputBinding:
      prefix: --tables_output_dir

  inputs_yaml:
    type: File
    inputBinding:
      prefix: --inputs_yaml_path

  family_types_A:
    type: File
    inputBinding:
      prefix: --family_types_A_path

  family_types_B:
    type: File
    inputBinding:
      prefix: --family_types_B_path

  family_sizes:
    type: File
    inputBinding:
      prefix: --family_sizes_path

outputs:

  title_page:
    type: File
    outputBinding:
      glob: 'title_page.pdf'

  read_counts:
    type: File
    outputBinding:
      glob: 'read_counts.pdf'

  align_rate:
    type: File
    outputBinding:
      glob: 'align_rate.pdf'

  on_target_rate:
    type: File
    outputBinding:
      glob: 'on_target_rate.pdf'

  gc_cov_each_sample:
    type: File
    outputBinding:
      glob: 'gc_cov_each_sample.pdf'

  insert_sizes:
    type: File
    outputBinding:
      glob: 'insert_sizes.pdf'

  coverage_per_interval:
    type: File
    outputBinding:
      glob: 'coverage_per_interval.pdf'

  coverage_per_interval_exon_level:
    type: File
    outputBinding:
      glob: 'coverage_per_interval_exon_level.pdf'

  cov_and_family_type_A:
    type: File
    outputBinding:
      glob: 'a_targets_cov_and_family_types.pdf'

  cov_and_family_type_B:
    type: File
    outputBinding:
      glob: 'b_targets_cov_and_family_types.pdf'

  family_sizes_all:
    type: File
    outputBinding:
      glob: 'family_sizes_all.pdf'

  family_sizes_simplex:
    type: File
    outputBinding:
      glob: 'family_sizes_simplex.pdf'

  family_sizes_duplex:
    type: File
    outputBinding:
      glob: 'family_sizes_duplex.pdf'

  pipeline_inputs:
    type: File
    outputBinding:
      glob: 'pipeline_inputs.pdf'
