cwlVersion: v1.0

class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_params/schemas/mutect.yaml
      - $import: ../resources/run_params/schemas/vardict.yaml
      - $import: ../resources/run_params/schemas/basic-filtering-vardict.yaml
      - $import: ../resources/run_params/schemas/basic-filtering-mutect.yaml
      - $import: ../resources/run_params/schemas/bcftools.yaml
      - $import: ../resources/run_tools/ACCESS_variants_run_tools.yaml

inputs:

  run_tools: ../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools

  mutect_params: ../resources/run_params/schemas/mutect.yaml#mutect_params
  vardict_params: ../resources/run_params/schemas/vardict.yaml#vardict_params
  basicfiltering_vardict_params: ../resources/run_params/schemas/basic-filtering-vardict.yaml#basicfiltering_vardict_params
  basicfiltering_mutect_params: ../resources/run_params/schemas/basic-filtering-mutect.yaml#basicfiltering_mutect_params
  bcftools_params: ../resources/run_params/schemas/bcftools.yaml#bcftools_params

  tumor_bams:
    type: File[]
    secondaryFiles: [^.bai]
  normal_bams:
    type: File[]
    secondaryFiles: [^.bai]

  tumor_sample_names: string[]
  normal_sample_names: string[]

  bed_file: File

  ref_fasta:
    type: File
    secondaryFiles: [.fai, ^.dict]
  dbsnp:
    type: File
    secondaryFiles: [.idx]
  cosmic:
    type: File
    secondaryFiles: [.idx]

  annotate_concat_header_file: File

outputs:

  concatenated_vcf:
    type: File[]
    outputSource: concatenate/combined_vcf

  annotated_concatenated_vcf:
    type: File[]
    outputSource: concatenate/annotated_combined_vcf

  mutect_vcf:
    type: File[]
    outputSource: call_variants/mutect_vcf

  mutect_callstats:
    type: File[]
    outputSource: call_variants/mutect_callstats

  vardict_vcf:
    type: File[]
    outputSource: call_variants/vardict_vcf

  mutect_normalized_vcf:
    type: File[]
    outputSource: filtering/mutect_norm_vcf

  vardict_normalized_vcf:
    type: File[]
    outputSource: filtering/vardict_norm_vcf

steps:

  call_variants:
    run: ./subworkflows/call_variants.cwl
    in:
      run_tools: run_tools
      mutect_params: mutect_params
      vardict_params: vardict_params
      tumor_bam: tumor_bams
      normal_bam: normal_bams
      tumor_sample_name: tumor_sample_names
      normal_sample_name: normal_sample_names
      bed_file: bed_file
      dbsnp: dbsnp
      cosmic: cosmic
      reference_fasta: ref_fasta
    out: [mutect_vcf, vardict_vcf, mutect_callstats]
    scatter: [tumor_bam, normal_bam, tumor_sample_name, normal_sample_name]
    scatterMethod: dotproduct

  filtering:
    run: ./subworkflows/filtering.cwl
    in:
      basicfiltering_vardict_params: basicfiltering_vardict_params
      basicfiltering_mutect_params: basicfiltering_mutect_params
      vardict_vcf: call_variants/vardict_vcf
      mutect_vcf: call_variants/mutect_vcf
      tumor_sample_name: tumor_sample_names
      normal_sample_name: normal_sample_names
      ref_fasta: ref_fasta
      # Todo: is this needed?: For what?
      mutect_callstats: call_variants/mutect_callstats
    out: [vardict_norm_vcf, mutect_norm_vcf]
    scatter: [vardict_vcf, mutect_vcf, mutect_callstats, tumor_sample_name, normal_sample_name]
    scatterMethod: dotproduct

  concatenate:
    run: ./subworkflows/vcf_concat.cwl
    in:
      run_tools: run_tools
      bcftools_params: bcftools_params
      vcf_vardict: filtering/vardict_norm_vcf
      vcf_mutect: filtering/mutect_norm_vcf
      tumor_sample_name: tumor_sample_names
      normal_sample_name: normal_sample_names
      annotate_concat_input_header: annotate_concat_header_file
    out: [combined_vcf, annotated_combined_vcf]
    scatter: [vcf_vardict, vcf_mutect, tumor_sample_name, normal_sample_name]
    scatterMethod: dotproduct
