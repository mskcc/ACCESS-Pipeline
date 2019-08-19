cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_params/schemas/gbcms_params.yaml
      - $import: ../resources/run_tools/ACCESS_variants_run_tools.yaml

inputs:

  run_tools: ../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools
  gbcms_params: ../resources/run_params/schemas/gbcms_params.yaml#gbcms_params

  project_name: string
  title_file: File
  custom_enst_file: File
  all_maf:
    type: File[]

  ref_fasta:
    type: File
    secondaryFiles: [.fai]

  traceback_sample_ids:
    type: string[]

  traceback_bams:
    type: File[]
    secondaryFiles:
      - ^.bai

  traceback_input_mutations:
    type: File

outputs:
  collated_maf:
    type: File
    outputSource: maf_collate/collated_maf

  filtered_exonic:
    type: File
    outputSource: maf2tsv/filtered_exonic

  dropped_exonic:
    type: File
    outputSource: maf2tsv/dropped_exonic

  filtered_silent:
    type: File
    outputSource: maf2tsv/filtered_silent

  dropped_silent:
    type: File
    outputSource: maf2tsv/dropped_silent

  filtered_exonic_nonpanel:
    type: File
    outputSource: maf2tsv/filtered_exonic_nonpanel

  dropped_exonic_nonpanel:
    type: File
    outputSource: maf2tsv/dropped_exonic_nonpanel

  filtered_silent_nonpanel:
    type: File
    outputSource: maf2tsv/filtered_silent_nonpanel

  dropped_silent_nonpanel:
    type: File
    outputSource: maf2tsv/dropped_silent_nonpanel
  
  traceback_genotype_inputs:
    type: File
    outputSource: traceback_inputs/traceback_genotype_inputs

  tb_fillout_out:
    type: File
    outputSource: traceback_fillout/tb_fillout_out
  
  traceback_final:
    type: File
    outputSource: traceback_integrate/traceback_final

  tb_exonic_filtered_mutations:
    type: File
    outputSource: traceback_integrate/tb_exonic_filtered_mutations

  tb_exonic_dropped_mutations:
    type: File
    outputSource: traceback_integrate/tb_exonic_dropped_mutations

  tb_silent_filtered_mutations:
    type: File
    outputSource: traceback_integrate/tb_silent_filtered_mutations

  tb_silent_dropped_mutations:
    type: File
    outputSource: traceback_integrate/tb_silent_dropped_mutations


steps:
  maf_collate:
    run: ../cwl_tools/python/maf_collate.cwl
    in:
      all_maf: all_maf
      project_name: project_name
    out: [collated_maf]

  maf2tsv:
    run: ../cwl_tools/python/maf2tsv.cwl
    in:
      title_file: title_file
      collated_maf: maf_collate/collated_maf
      canonical_transcript_reference_file: custom_enst_file
    out: [
      filtered_exonic,
      dropped_exonic,
      filtered_silent,
      dropped_silent,
      filtered_exonic_nonpanel,
      dropped_exonic_nonpanel,
      filtered_silent_nonpanel,
      dropped_silent_nonpanel]

  traceback_inputs:
    run: ../cwl_tools/traceback/traceback_inputs.cwl
    in:
      title_file: title_file
      exonic_filtered_mutations: maf2tsv/filtered_exonic
      silent_filtered_mutations: maf2tsv/filtered_silent
      traceback_input_mutations: traceback_input_mutations
    out: [traceback_genotype_inputs]

  traceback_fillout:
    run: ../cwl_tools/traceback/gbcm_traceback.cwl
    in:
      run_tools: run_tools
      gbcms:
        valueFrom: $(inputs.run_tools.gbcms)
      gbcms_params: gbcms_params
      traceback_inputs_maf: traceback_inputs/traceback_genotype_inputs
      Traceback_ids: traceback_sample_ids
      Traceback_bam_files: traceback_bams
      ref_fasta: ref_fasta
      output:
        valueFrom: $('traceback_out.maf')
      omaf:
        valueFrom: $(inputs.gbcms_params.omaf)
      filter_duplicate:
        valueFrom: $(inputs.gbcms_params.filter_duplicate)
      thread:
        valueFrom: $(inputs.gbcms_params.thread)
      maq:
        valueFrom: $(inputs.gbcms_params.maq)
      fragment_count:
        valueFrom: $(inputs.gbcms_params.fragment_count)
    out: [tb_fillout_out]

  traceback_integrate:
    run: ../cwl_tools/traceback/traceback_integrate.cwl
    in:
      title_file: title_file
      exonic_filtered_mutations: maf2tsv/filtered_exonic
      exonic_dropped_mutations: maf2tsv/dropped_exonic
      silent_filtered_mutations: maf2tsv/filtered_silent
      silent_dropped_mutations: maf2tsv/dropped_silent
      traceback_input_maf: traceback_inputs/traceback_genotype_inputs
      traceback_out_maf: traceback_fillout/tb_fillout_out
    out: [
      traceback_final,
      tb_exonic_filtered_mutations,
      tb_exonic_dropped_mutations,
      tb_silent_filtered_mutations,
      tb_silent_dropped_mutations]