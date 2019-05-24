cwlVersion: v1.0

class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_params/schemas/mutect.yaml
      - $import: ../resources/run_params/schemas/vardict.yaml
      - $import: ../resources/run_params/schemas/basic-filtering-vardict.yaml
      - $import: ../resources/run_params/schemas/basic-filtering-mutect.yaml
      - $import: ../resources/run_params/schemas/bcftools.yaml
      - $import: ../resources/run_params/schemas/vcf2maf.yaml
      - $import: ../resources/run_params/schemas/gbcms_params.yaml
      - $import: ../resources/run_params/schemas/access_filters.yaml
      - $import: ../resources/run_params/schemas/delly.yaml
      - $import: ../resources/run_tools/schemas.yaml

inputs:

  project_name: string
  version: string

  mutect_params: ../resources/run_params/schemas/mutect.yaml#mutect_params
  vardict_params: ../resources/run_params/schemas/vardict.yaml#vardict_params
  basicfiltering_vardict_params: ../resources/run_params/schemas/basic-filtering-vardict.yaml#basicfiltering_vardict_params
  basicfiltering_mutect_params: ../resources/run_params/schemas/basic-filtering-mutect.yaml#basicfiltering_mutect_params
  bcftools_params: ../resources/run_params/schemas/bcftools.yaml#bcftools_params
  vcf2maf_params: ../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params
  gbcms_params: ../resources/run_params/schemas/gbcms_params.yaml#gbcms_params
  access_filters_params: ../resources/run_params/schemas/access_filters.yaml#access_filters__params
  delly_params: ../resources/run_params/schemas/delly.yaml#delly_params
  sv_run_tools: ../resources/run_tools/sv.yaml#run_tools

  hotspots: File

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
  matched_normal_ids: string[]
  genotyping_bams_ids: string[]

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
  sv_normal_bam: File[]

outputs:

  concatenated_vcf:
    type: File[]
    outputSource: snps_and_indels/concatenated_vcf

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

  hotspots_filtered_maf:
    type: File[]
    outputSource: snps_and_indels/hotspots_filtered_maf

  consolidated_maf:
    type: File[]
    outputSource: snps_and_indels/consolidated_maf

  fillout_maf:
    type: File[]
    outputSource: snps_and_indels/fillout_maf

  final_filtered_maf:
    type: File[]
    outputSource: snps_and_indels/final_filtered_maf

  delly_sv:
    type:
      type: array
      items:
        type: array
        items: File
    outputSource: structural_variants/delly_sv

  delly_filtered_sv:
    type:
      type: array
      items:
        type: array
        items: File
    outputSource: structural_variants/delly_filtered_sv

  merged_structural_variants:
    type: File[]
    outputSource: structural_variants/merged_structural_variants

  merged_structural_variants_unfiltered:
    type: File[]
    outputSource: structural_variants/merged_structural_variants_unfiltered

  structural_variants_maf:
    type: File[]
    outputSource: structural_variants/structural_variants_maf

steps:

  ###################
  # SNPs and Indels #
  ###################

  snps_and_indels:
    run: ./subworkflows/snps_and_indels.cwl
    in:
      mutect_params: mutect_params
      vardict_params: vardict_params
      basicfiltering_vardict_params: basicfiltering_vardict_params
      basicfiltering_mutect_params: basicfiltering_mutect_params
      bcftools_params: bcftools_params
      vcf2maf_params: vcf2maf_params
      gbcms_params: gbcms_params
      access_filters_params: access_filters_params

      tumor_bams: tumor_bams
      normal_bams: normal_bams
      tumor_sample_names: tumor_sample_names
      normal_sample_names: normal_sample_names
      matched_normal_ids: matched_normal_ids
      bed_file: bed_file
      refseq: refseq
      ref_fasta: ref_fasta
      dbsnp: dbsnp
      cosmic: cosmic
      hotspots: hotspots
      combine_vcf: module_3/concatenated_vcf
      genotyping_bams: genotyping_bams
      genotyping_bams_ids: genotyping_bams_ids
      tumor_sample_name: tumor_sample_names
      normal_sample_name: normal_sample_names
      ref_fasta: ref_fasta
      exac_filter: exac_filter
    out: [
      concatenated_vcf,
      mutect_vcf,
      mutect_callstats,
      vardict_vcf,
      mutect_normalized_vcf,
      vardict_normalized_vcf,
      final_maf,
      hotspots_filtered_maf,
      consolidated_maf,
      fillout_maf,
      final_filtered_maf]

  #######################
  # Structural Variants #
  #######################

#  structural_variants:
#    run: ./module-6.cwl
#    in:
#      delly_params: delly_params
#      vcf2maf_params: vcf2maf_params
#      tumor_bam: tumor_bams
#      normal_bam: normal_bams
#      normal_sample_name: tumor_sample_names
#      tumor_sample_name: normal_sample_names
#      reference_fasta: ref_fasta
#      exac_filter: exac_filter
#      delly_type:
#        valueFrom: $(['DEL', 'DUP', 'BND', 'INV', 'INS'])
#      vep_data:
#        valueFrom: $(inputs.vcf2maf_params.vep_data)
#    out: [
#      delly_sv,
#      delly_filtered_sv,
#      merged_structural_variants,
#      merged_structural_variants_unfiltered,
#      structural_variants_maf,
#      final_filtered_maf]
#    scatter: [tumor_bam, normal_bam, tumor_sample_name, normal_sample_name]
#    scatterMethod: dotproduct

  manta:
    run: ./subworkflows/manta.cwl
    in:
      sv_sample_id: sv_sample_id
      sv_tumor_bams: sv_tumor_bams
      sv_normal_bam: sv_normal_bam
      sv_run_tools: sv_run_tools
      project_name: project_name
      version: version
    out: [
      sv_directory,
      annotated_sv_file,
      concatenated_vcf]
