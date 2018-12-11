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
      - $import: ../resources/run_params/schemas/vcf2maf.yaml
      - $import: ../resources/run_params/schemas/gbcms_params.yaml

inputs:

  vcf2maf_params: ../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params
  gbcms_params: ../resources/run_params/schemas/gbcms_params.yaml#gbcms_params

  hotspots: File
  combine_vcf: File
  tumor_sample_name: string
  normal_sample_name: string

  genotyping_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
  genotyping_bams_ids: string[]

  hotspot_list: File
  ref_fasta:
    type: File
    secondaryFiles: [.fai]

outputs:

  maf:
    type: File
    outputSource: vcf2maf/output

  hotspots_filtered_maf:
    type: File
    outputSource: tag_hotspots/hotspot_tagged_maf

  consolidated_maf:
    type: File
    outputSource: remove_variants/consolidated_maf

  fillout_maf:
    type: File
    outputSource: fillout/fillout_out

steps:

  vcf2maf:
    run: ../cwl_tools/vcf2maf/vcf2maf.cwl
    in:
      vcf2maf_params: vcf2maf_params
      input_vcf: combine_vcf

      # Todo: are these right?
      vcf_tumor_id: tumor_sample_name
      vcf_normal_id: normal_sample_name
      tumor_id: tumor_sample_name
      normal_id: normal_sample_name
      ref_fasta: ref_fasta

      species:
        valueFrom: $(inputs.vcf2maf_params.species)
      ncbi_build:
        valueFrom: $(inputs.vcf2maf_params.ncbi_build)
      maf_center:
        valueFrom: $(inputs.vcf2maf_params.maf_center)
      max_filter_ac:
        valueFrom: $(inputs.vcf2maf_params.max_filter_ac)
      min_hom_vaf:
        valueFrom: $(inputs.vcf2maf_params.min_hom_vaf)
      filter_vcf:
        valueFrom: $(inputs.vcf2maf_params.filter_vcf)
      vep_path:
        valueFrom: $(inputs.vcf2maf_params.vep_path)
      vep_data:
        valueFrom: $(inputs.vcf2maf_params.vep_data)
      vep_forks:
        valueFrom: $(inputs.vcf2maf_params.vep_forks)
      retain_info:
        valueFrom: $(inputs.vcf2maf_params.retain_info)
      buffer_size:
        valueFrom: $(inputs.vcf2maf_params.buffer_size)
      custom_enst:
        valueFrom: $(inputs.vcf2maf_params.custom_enst)

      output_maf:
        valueFrom: $(inputs.tumor_id + '.' + inputs.normal_id + '_combinedVariants_vep.maf')
    out: [output]

  tag_hotspots:
    run: ../cwl_tools/hotspots/tag_hotspots.cwl
    in:
      input_maf: vcf2maf/output
      input_hotspot: hotspots
      output_maf:
        valueFrom: $(inputs.input_maf.basename.replace('.maf', '_taggedHotspots.maf'))
    out:
      [hotspot_tagged_maf]

  remove_variants:
    run: ../cwl_tools/remove_variants/remove_variants.cwl
    in:
      input_maf: tag_hotspots/hotspot_tagged_maf
      output_maf:
        valueFrom: $(inputs.input_maf.basename.replace('.maf', '_rmv.maf'))
    out: [consolidated_maf]

  fillout:
    run: ../cwl_tools/gbcms/gbcms.cwl
    in:
      gbcms_params: gbcms_params
      maf: remove_variants/consolidated_maf
      genotyping_bams_ids: genotyping_bams_ids
      bams:
        source: genotyping_bams
        # Todo: Why doesn't b.path work? Because of --linkImports?
        valueFrom: $(self.map(function(b, i) {return inputs.genotyping_bams_ids[i] + ':' + b.location.replace('file://', '')}))
      ref_fasta: ref_fasta
      output:
        valueFrom: $(inputs.maf.basename.replace('.maf', '_fillout.maf'))
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
    out: [fillout_out]

#  ngs_filters:
#    run: ngs-filters/1.3/ngs-filters.cwl
#    in:
#      tumor_sample_name: tumor_sample_name
#      normal_sample_name: normal_sample_name
#      inputMaf: fillout_tumor_normal/portal_fillout
#      outputMaf:
#        valueFrom: ${ return inputs.tumor_sample_name + "." + inputs.normal_sample_name + ".muts.maf" }
#      NormalPanelMaf: fillout_second/fillout_curated_bams
#      inputHSP: hotspot_list
#    out: [output]
