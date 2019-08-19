cwlVersion: v1.0

class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_params/schemas/mutect.yaml
      - $import: ../../resources/run_params/schemas/vardict.yaml
      - $import: ../../resources/run_params/schemas/basic-filtering-vardict.yaml
      - $import: ../../resources/run_params/schemas/basic-filtering-mutect.yaml
      - $import: ../../resources/run_params/schemas/bcftools.yaml
      - $import: ../../resources/run_params/schemas/vcf2maf.yaml
      - $import: ../../resources/run_params/schemas/gbcms_params.yaml
      - $import: ../../resources/run_params/schemas/access_filters.yaml
      - $import: ../../resources/run_tools/ACCESS_variants_run_tools.yaml
      - $import: ../../resources/run_tools/traceback.yaml

inputs:

  project_name: string
  version: string
  run_tools: ../../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools
  traceback: ../../resources/run_tools/traceback.yaml#traceback

  mutect_params: ../../resources/run_params/schemas/mutect.yaml#mutect_params
  vardict_params: ../../resources/run_params/schemas/vardict.yaml#vardict_params
  basicfiltering_vardict_params: ../../resources/run_params/schemas/basic-filtering-vardict.yaml#basicfiltering_vardict_params
  basicfiltering_mutect_params: ../../resources/run_params/schemas/basic-filtering-mutect.yaml#basicfiltering_mutect_params
  bcftools_params: ../../resources/run_params/schemas/bcftools.yaml#bcftools_params
  vcf2maf_params: ../../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params
  gbcms_params: ../../resources/run_params/schemas/gbcms_params.yaml#gbcms_params
  access_filters_params: ../../resources/run_params/schemas/access_filters.yaml#access_filters__params

  hotspots: File
  blacklist_file: File
  custom_enst_file: File
  annotate_concat_header_file: File
  title_file: File

  #########################################
  # Tumor bams should be sorted in paired #
  # order with Normal bams                #
  #########################################
  tumor_bams:
    type: File[]
    secondaryFiles: [^.bai]
  normal_bams:
    type: File[]
    secondaryFiles: [^.bai]
  genotyping_bams:
    type: File[]
    secondaryFiles: [^.bai]
  traceback: traceback
  # traceback_bams:
  #   valueFrom: $(inputs.Traceback.bam_files)
  #   type: File[]
  #   secondaryFiles: [^.bai]

  tumor_sample_names: string[]
  normal_sample_names: string[]
  genotyping_bams_ids: string[]
  matched_normal_ids: string[]
  # traceback_sample_ids:
  #   valueFrom: $(inputs.Traceback.ids)
  #   type: string[]

  # traceback_input_mutations:
  #   valueFrom: $(inputs.Traceback.traceback_mutation_file)
  #   type: File
  bed_file: File
  refseq: File

  dbsnp:
    type: File
    secondaryFiles: [.idx]
  cosmic:
    type: File
    secondaryFiles: [.idx]
  ref_fasta:
    type: File
    secondaryFiles: [.fai, ^.dict]
  exac_filter:
    type: File
    secondaryFiles:
      - .tbi

outputs:

  concatenated_vcf:
    type: File[]
    outputSource: module_3/concatenated_vcf

  annotated_concatenated_vcf:
    type: File[]
    outputSource: module_3/annotated_concatenated_vcf

  mutect_vcf:
    type: File[]
    outputSource: module_3/mutect_vcf

  mutect_callstats:
    type: File[]
    outputSource: module_3/mutect_callstats

  vardict_vcf:
    type: File[]
    outputSource: module_3/vardict_vcf

  mutect_normalized_vcf:
    type: File[]
    outputSource: module_3/mutect_normalized_vcf

  vardict_normalized_vcf:
    type: File[]
    outputSource: module_3/vardict_normalized_vcf

  final_maf:
    type: File[]
    outputSource: module_4/maf

  kept_rmvbyanno_maf:
    type: File[]
    outputSource: module_4/kept_rmvbyanno_maf

  dropped_rmvbyanno_maf:
    type: File[]
    outputSource: module_4/dropped_rmvbyanno_maf

  dropped_NGR_rmvbyanno_maf:
    type: File[]
    outputSource: module_4/dropped_NGR_rmvbyanno_maf

  hotspots_filtered_maf:
    type: File[]
    outputSource: module_4/hotspots_filtered_maf

  fillout_maf:
    type: File[]
    outputSource: module_4/fillout_maf

  final_filtered_maf:
    type: File[]
    outputSource: module_4/final_filtered_maf

  final_filtered_condensed_maf:
    type: File[]
    outputSource: module_4/final_filtered_condensed_maf

  collated_maf:
    type: File
    outputSource: module_5/collated_maf

  filtered_exonic:
    type: File
    outputSource: module_5/filtered_exonic

  dropped_exonic:
    type: File
    outputSource: module_5/dropped_exonic

  filtered_silent:
    type: File
    outputSource: module_5/filtered_silent

  dropped_silent:
    type: File
    outputSource: module_5/dropped_silent

  filtered_exonic_nonpanel:
    type: File
    outputSource: module_5/filtered_exonic_nonpanel

  dropped_exonic_nonpanel:
    type: File
    outputSource: module_5/dropped_exonic_nonpanel

  filtered_silent_nonpanel:
    type: File
    outputSource: module_5/filtered_silent_nonpanel

  dropped_silent_nonpanel:
    type: File
    outputSource: module_5/dropped_silent_nonpanel
  
  traceback_genotype_inputs:
    type: File
    outputSource: module_5/traceback_genotype_inputs
  
  tb_fillout_out:
    type: File
    outputSource: module_5/tb_fillout_out
  
  traceback_final:
    type: File
    outputSource: module_5/traceback_final
  
  tb_exonic_filtered_mutations:
    type: File
    outputSource: module_5/tb_exonic_filtered_mutations

  tb_exonic_dropped_mutations:
    type: File
    outputSource: module_5/tb_exonic_dropped_mutations

  tb_silent_filtered_mutations:
    type: File
    outputSource: module_5/tb_silent_filtered_mutations

  tb_silent_dropped_mutations:
    type: File
    outputSource: module_5/tb_silent_dropped_mutations

steps:

  ###################
  # Variant Calling #
  ###################

  module_3:
    run: ../module-3.cwl
    in:
      run_tools: run_tools
      tumor_bams: tumor_bams
      normal_bams: normal_bams
      tumor_sample_names: tumor_sample_names
      normal_sample_names: normal_sample_names
      bed_file: bed_file
      refseq: refseq
      ref_fasta: ref_fasta
      dbsnp: dbsnp
      cosmic: cosmic
      mutect_params: mutect_params
      vardict_params: vardict_params
      basicfiltering_vardict_params: basicfiltering_vardict_params
      basicfiltering_mutect_params: basicfiltering_mutect_params
      bcftools_params: bcftools_params
      annotate_concat_header_file: annotate_concat_header_file
    out: [
      concatenated_vcf,
      annotated_concatenated_vcf,
      mutect_vcf,
      mutect_callstats,
      vardict_vcf,
      mutect_normalized_vcf,
      vardict_normalized_vcf]

  ##############
  # Genotyping #
  ##############

  module_4:
    run: ../module-4.cwl
    in:
      run_tools: run_tools
      vcf2maf_params: vcf2maf_params
      access_filters_params: access_filters_params
      hotspots: hotspots
      blacklist_file: blacklist_file
      custom_enst_file: custom_enst_file
      gbcms_params: gbcms_params
      combine_vcf: module_3/annotated_concatenated_vcf
      genotyping_bams: genotyping_bams
      genotyping_bams_ids: genotyping_bams_ids
      tumor_sample_name: tumor_sample_names
      normal_sample_name: normal_sample_names
      matched_normal_sample_name: matched_normal_ids
      ref_fasta: ref_fasta
      exac_filter: exac_filter
    out: [
      maf,
      kept_rmvbyanno_maf,
      dropped_rmvbyanno_maf,
      dropped_NGR_rmvbyanno_maf,
      hotspots_filtered_maf,
      fillout_maf,
      final_filtered_maf,
      final_filtered_condensed_maf]
    scatter: [combine_vcf, tumor_sample_name, normal_sample_name, matched_normal_sample_name]
    scatterMethod: dotproduct

  ####################################
  # Convert maf to tsv and traceback #
  ####################################

  module_5:
    run: ../module-5.cwl
    in:
      project_name: project_name
      custom_enst_file: custom_enst_file
      all_maf: module_4/final_filtered_maf
      title_file: title_file
      gbcms_params: gbcms_params
      run_tools: run_tools
      traceback_sample_ids:
        valueFrom: $(traceback.ids)
      traceback_bams:
        valueFrom: $(traceback.bam_files)
      traceback_input_mutations:
        valueFrom: $(traceback.traceback_mutation_file)
      ref_fasta: ref_fasta
    out: [
        collated_maf,
        filtered_exonic,
        dropped_exonic,
        filtered_silent,
        dropped_silent,
        filtered_exonic_nonpanel,
        dropped_exonic_nonpanel,
        filtered_silent_nonpanel,
        dropped_silent_nonpanel,
        traceback_genotype_inputs,
        tb_fillout_out,
        traceback_final,
        tb_exonic_filtered_mutations,
        tb_exonic_dropped_mutations,
        tb_silent_filtered_mutations,
        tb_silent_dropped_mutations]
