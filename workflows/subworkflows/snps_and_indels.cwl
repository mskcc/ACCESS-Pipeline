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

inputs:

  tmp_dir: Directory
  project_name: string
  version: string
  run_tools: ../../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools

  mutect_params: ../../resources/run_params/schemas/mutect.yaml#mutect_params
  vardict_params: ../../resources/run_params/schemas/vardict.yaml#vardict_params
  basicfiltering_vardict_params: ../../resources/run_params/schemas/basic-filtering-vardict.yaml#basicfiltering_vardict_params
  basicfiltering_mutect_params: ../../resources/run_params/schemas/basic-filtering-mutect.yaml#basicfiltering_mutect_params
  bcftools_params: ../../resources/run_params/schemas/bcftools.yaml#bcftools_params
  vcf2maf_params: ../../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params
  gbcms_params: ../../resources/run_params/schemas/gbcms_params.yaml#gbcms_params
  access_filters_params: ../../resources/run_params/schemas/access_filters.yaml#access_filters__params

  hotspots: File
  custom_enst_file: File
  annotate_concat_header_file: File

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

  tumor_sample_names: string[]
  normal_sample_names: string[]
  genotyping_bams_ids: string[]
  matched_normal_ids: string[]

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

steps:

  ###################
  # Variant Calling #
  ###################

  module_3:
    run: ../module-3.cwl
    in:
      tmp_dir: tmp_dir
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
      tmp_dir: tmp_dir
      hotspots: hotspots
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
    out: [maf, kept_rmvbyanno_maf, dropped_rmvbyanno_maf, dropped_NGR_rmvbyanno_maf, hotspots_filtered_maf, fillout_maf, final_filtered_maf]
    scatter: [combine_vcf, tumor_sample_name, normal_sample_name, matched_normal_sample_name]
    scatterMethod: dotproduct
