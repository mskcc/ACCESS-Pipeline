cwlVersion: v1.0

class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_tools/ACCESS_variants_run_tools.yaml
      - $import: ../resources/run_params/schemas/mutect.yaml
      - $import: ../resources/run_params/schemas/vardict.yaml
      - $import: ../resources/run_params/schemas/basic-filtering-vardict.yaml
      - $import: ../resources/run_params/schemas/basic-filtering-mutect.yaml
      - $import: ../resources/run_params/schemas/bcftools.yaml
      - $import: ../resources/run_params/schemas/vcf2maf.yaml
      - $import: ../resources/run_params/schemas/gbcms_params.yaml
      - $import: ../resources/run_params/schemas/access_filters.yaml
      - $import: ../resources/run_tools/schemas.yaml

inputs:

  project_name: string
  version: string
  run_tools: ../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools

  mutect_params: ../resources/run_params/schemas/mutect.yaml#mutect_params
  vardict_params: ../resources/run_params/schemas/vardict.yaml#vardict_params
  basicfiltering_vardict_params: ../resources/run_params/schemas/basic-filtering-vardict.yaml#basicfiltering_vardict_params
  basicfiltering_mutect_params: ../resources/run_params/schemas/basic-filtering-mutect.yaml#basicfiltering_mutect_params
  bcftools_params: ../resources/run_params/schemas/bcftools.yaml#bcftools_params
  vcf2maf_params: ../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params
  gbcms_params: ../resources/run_params/schemas/gbcms_params.yaml#gbcms_params
  access_filters_params: ../resources/run_params/schemas/access_filters.yaml#access_filters__params

  hotspots: File
  blacklist_file: File
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

  sv_sample_id: string[]
  sv_tumor_bams: File[]
  sv_normal_bam: File
  sv_run_tools: ../resources/run_tools/schemas.yaml#sv_run_tools

outputs:

  concatenated_vcf:
    type: File[]
    outputSource: snps_and_indels/concatenated_vcf

  annotated_concatenated_vcf:
    type: File[]
    outputSource: snps_and_indels/annotated_concatenated_vcf

  mutect_vcf:
    type: File[]
    outputSource: snps_and_indels/mutect_vcf

  mutect_callstats:
    type: File[]
    outputSource: snps_and_indels/mutect_callstats

  vardict_vcf:
    type: File[]
    outputSource: snps_and_indels/vardict_vcf

  mutect_normalized_vcf:
    type: File[]
    outputSource: snps_and_indels/mutect_normalized_vcf

  vardict_normalized_vcf:
    type: File[]
    outputSource: snps_and_indels/vardict_normalized_vcf

  final_maf:
    type: File[]
    outputSource: snps_and_indels/final_maf

  kept_rmvbyanno_maf:
    type: File[]
    outputSource: snps_and_indels/kept_rmvbyanno_maf

  dropped_rmvbyanno_maf:
    type: File[]
    outputSource: snps_and_indels/dropped_rmvbyanno_maf

  dropped_NGR_rmvbyanno_maf:
    type: File[]
    outputSource: snps_and_indels/dropped_NGR_rmvbyanno_maf

  hotspots_filtered_maf:
    type: File[]
    outputSource: snps_and_indels/hotspots_filtered_maf

  fillout_maf:
    type: File[]
    outputSource: snps_and_indels/fillout_maf

  final_filtered_maf:
    type: File[]
    outputSource: snps_and_indels/final_filtered_maf

  final_filtered_condensed_maf:
    type: File[]
    outputSource: snps_and_indels/final_filtered_condensed_maf

  # Manta

  sv_directory:
    type: Directory[]
    outputSource: manta/sv_directory

  annotated_sv_file:
    type: File[]
    outputSource: manta/annotated_sv_file

  concatenated_vcf:
    type: File
    outputSource: manta/concatenated_vcf

steps:

  ###################
  # SNPs and Indels #
  ###################

  snps_and_indels:
    run: ./subworkflows/snps_and_indels.cwl
    in:
      project_name: project_name
      version: version
      run_tools: run_tools
      mutect_params: mutect_params
      vardict_params: vardict_params
      basicfiltering_vardict_params: basicfiltering_vardict_params
      basicfiltering_mutect_params: basicfiltering_mutect_params
      bcftools_params: bcftools_params
      vcf2maf_params: vcf2maf_params
      gbcms_params: gbcms_params
      access_filters_params: access_filters_params
      hotspots: hotspots
      blacklist_file: blacklist_file
      custom_enst_file: custom_enst_file
      annotate_concat_header_file: annotate_concat_header_file
      tumor_bams: tumor_bams
      normal_bams: normal_bams
      genotyping_bams: genotyping_bams
      tumor_sample_names: tumor_sample_names
      normal_sample_names: normal_sample_names
      genotyping_bams_ids: genotyping_bams_ids
      matched_normal_ids: matched_normal_ids
      bed_file: bed_file
      refseq: refseq
      dbsnp: dbsnp
      cosmic: cosmic
      ref_fasta: ref_fasta
      exac_filter: exac_filter
    out: [
      concatenated_vcf,
      annotated_concatenated_vcf,
      mutect_vcf,
      mutect_callstats,
      vardict_vcf,
      mutect_normalized_vcf,
      vardict_normalized_vcf,
      final_maf,
      kept_rmvbyanno_maf,
      dropped_rmvbyanno_maf,
      dropped_NGR_rmvbyanno_maf,
      hotspots_filtered_maf,
      fillout_maf,
      final_filtered_maf,
      final_filtered_condensed_maf,
    ]

  #######################
  # Structural Variants #
  #######################

  manta:
    run: ./subworkflows/manta.cwl
    in:
      sample_id: sv_sample_id
      tumor_bams: sv_tumor_bams
      normal_bam: sv_normal_bam
      run_tools: sv_run_tools
      reference_fasta: ref_fasta
      project_name: project_name
      version: version
    out: [
      sv_directory,
      annotated_sv_file,
      concatenated_vcf]
