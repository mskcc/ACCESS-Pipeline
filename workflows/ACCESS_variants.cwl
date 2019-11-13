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

  # CNV #
  file_path: string
  coverage_script: string
  copy_number_script: string
  loess_normalize_script: string
  tumor_sample_list: File
  normal_sample_list: File
  targets_coverage_bed: File
  targets_coverage_annotation: File
  reference_fasta: File
  threads: int

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

  collated_maf:
    type: File
    outputSource: snps_and_indels/collated_maf

  filtered_exonic:
    type: File
    outputSource: snps_and_indels/filtered_exonic

  dropped_exonic:
    type: File
    outputSource: snps_and_indels/dropped_exonic

  filtered_silent:
    type: File
    outputSource: snps_and_indels/filtered_silent

  dropped_silent:
    type: File
    outputSource: snps_and_indels/dropped_silent

  filtered_nonpanel:
    type: File
    outputSource: snps_and_indels/filtered_nonpanel

  dropped_nonpanel:
    type: File
    outputSource: snps_and_indels/dropped_nonpanel

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

  # Copy Number Variant Calling

  tumors_covg:
    type: File
    outputSource: cnv/tumors_covg

  normals_covg:
    type: File
    outputSource: cnv/normals_covg

  bam_list:
    type: File[]
    outputSource: cnv/bam_list

  coverage_std_out:
    type: File
    outputSource: cnv/coverage_std_out

  coverage_std_err:
    type: File
    outputSource: cnv/coverage_std_err

  tumor_loess_text:
    type: File
    outputSource: cnv/tumor_loess_text

  normal_loess_text:
    type: File
    outputSource: cnv/normal_loess_text

  tumor_loess_pdf:
    type: File
    outputSource: cnv/tumor_loess_pdf

  normal_loess_pdf:
    type: File
    outputSource: cnv/normal_loess_pdf

  loess_tumor_std_out:
    type: File
    outputSource: cnv/loess_tumor_std_out

  loess_tumor_std_err:
    type: File
    outputSource: cnv/loess_tumor_std_err

  loess_normal_std_out:
    type: File
    outputSource: cnv/loess_normal_std_out

  loess_normal_std_err:
    type: File
    outputSource: cnv/loess_normal_std_err

  genes_file:
    type: File
    outputSource: cnv/genes_file

  probes_file:
    type: File
    outputSource: cnv/probes_file

  intragenic_file:
    type: File
    outputSource: cnv/intragenic_file

  copy_pdf:
    type: File
    outputSource: cnv/copy_pdf

  seg_files:
    type: File[]
    outputSource: cnv/seg_files

  copy_standard_out:
    type: File
    outputSource: cnv/copy_standard_out

  copy_standard_err:
    type: File
    outputSource: cnv/copy_standard_err

steps:

  ###################
  # SNPs and Indels #
  ###################

  snps_and_indels:
    run: ./subworkflows/snps_and_indels.cwl
    in:
      project_name: project_name
      title_file: title_file
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
      collated_maf,
      filtered_exonic,
      dropped_exonic,
      filtered_silent,
      dropped_silent,
      filtered_nonpanel,
      dropped_nonpanel
    ]

  #######################
  # Structural Variants #
  #######################

  manta:
    run: ./subworkflows/manta.cwl
    in:
      sv_sample_id: sv_sample_id
      sv_tumor_bams: sv_tumor_bams
      sv_normal_bam: sv_normal_bam
      sv_run_tools: sv_run_tools
      ref_fasta: ref_fasta
      project_name: project_name
      version: version
    out: [
      sv_directory,
      annotated_sv_file,
      concatenated_vcf]

  ########################
  # Copy Number Variants #
  ########################

  cnv:
    run: ./subworkflows/call_cnv.cwl
    in:
      file_path: file_path
      coverage_script: coverage_script
      copy_number_script: copy_number_script
      loess_normalize_script: loess_normalize_script
      tumor_sample_list: tumor_sample_list
      normal_sample_list: normal_sample_list
      targets_coverage_bed: targets_coverage_bed
      targets_coverage_annotation: targets_coverage_annotation
      reference_fasta: reference_fasta
      project_name: project_name
      threads: threads
    out: [
      tumors_covg,
      normals_covg,
      bam_list,
      coverage_std_out,
      coverage_std_err,
      tumor_loess_text,
      normal_loess_text,
      tumor_loess_pdf,
      normal_loess_pdf,
      loess_tumor_std_out,
      loess_tumor_std_err,
      loess_normal_std_out,
      loess_normal_std_err,
      genes_file,
      probes_file,
      intragenic_file,
      copy_pdf,
      seg_files,
      copy_standard_out,
      copy_standard_err
    ]
