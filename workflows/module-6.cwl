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
      - $import: ../resources/run_params/schemas/delly.yaml

inputs:

  vcf2maf_params: ../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params
  delly_params: ../resources/run_params/schemas/delly.yaml#delly_params

  tmp_dir: Directory
  tumor_bam:
    type: File
    secondaryFiles: [^.bai]
  normal_bam:
    type: File
    secondaryFiles: [^.bai]

  normal_sample_name: string
  tumor_sample_name: string
  delly_type: string[]
  vep_data: string
  reference_fasta: File

  exac_filter:
    type: File
    secondaryFiles:
      - .tbi

outputs:

  delly_sv:
    type: File[]
    secondaryFiles:
      - ^.bcf.csi
    outputSource: call_sv_by_delly/delly_sv

  delly_filtered_sv:
    type: File[]
    outputBinding:
      glob: '*.pass.bcf'
    secondaryFiles:
      - ^.bcf.csi
    outputSource: call_sv_by_delly/delly_filtered_sv

  merged_structural_variants:
    type: File
    outputSource: merge_with_bcftools/merged_file

  merged_structural_variants_unfiltered:
    type: File
    outputSource: merge_with_bcftools_unfiltered/merged_file_unfiltered

  structural_variants_maf:
    type: File
    outputSource: vcf2maf/output

steps:

  #######################
  # Create pairing file #
  #######################

  createTNPair:
    in:
      tumor_sample_name: tumor_sample_name
      normal_sample_name: normal_sample_name
      echoString:
        valueFrom: $(inputs.tumor_sample_name + '\ttumor\n' + inputs.normal_sample_name + '\tcontrol')
      output_filename:
        valueFrom: $('tn_pair.txt')

    out: [pairfile]

    run:
      class: CommandLineTool
      baseCommand: [echo, -e]
      stdout: $(inputs.output_filename)
      requirements:
        InlineJavascriptRequirement: {}
        MultipleInputFeatureRequirement: {}

      inputs:
        echoString:
          type: string
          inputBinding:
              position: 1
        output_filename: string

      outputs:
        pairfile:
          type: stdout

  #####################
  # Call + Filter SVs #
  #####################

  call_sv_by_delly:
    scatter: [delly_type]
    scatterMethod: dotproduct

    in:
      delly_params: delly_params
      tumor_bam: tumor_bam
      normal_bam: normal_bam
      normal_sample_name: normal_sample_name
      tumor_sample_name: tumor_sample_name
      pairfile: createTNPair/pairfile
      delly_type: delly_type
      reference_fasta: reference_fasta
    out: [delly_sv, delly_filtered_sv]

    run:
      class: Workflow

      inputs:
        delly_params: ../resources/run_params/schemas/delly.yaml#delly_params
        tumor_bam: File
        normal_bam: File
        normal_sample_name: string
        tumor_sample_name: string
        delly_type: string
        pairfile: File
        reference_fasta: File

      outputs:
        delly_sv:
          type: File
          secondaryFiles:
            - ^.bcf.csi
          outputSource: delly_call/sv_file

        delly_filtered_sv:
#          type: File[]
          type: File
          outputBinding:
            glob: '*.pass.bcf'
          secondaryFiles: [^.bcf.csi]
          outputSource: delly_filter/sv_file

      steps:
        delly_call:
          run: ../cwl_tools/delly/delly_call.cwl
          in:
            delly_params: delly_params
            sv_type: delly_type
            tumor_bam: tumor_bam
            normal_bam: normal_bam
            normal_sample_name: normal_sample_name
            tumor_sample_name: tumor_sample_name
            reference_fasta: reference_fasta

            excluded_regions:
              valueFrom: $(inputs.delly_params.excluded_regions)

            output_filename:
              valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.' + inputs.sv_type + '.bcf')
          out: [sv_file]

        delly_filter:
          run: ../cwl_tools/delly/delly_filter.cwl
          in:
            delly_params: delly_params
            input_bcf: delly_call/sv_file
            sample_file: pairfile
            sv_type: delly_type

            filter_mode:
              valueFrom: $(inputs.delly_params.filter_mode)
            min_genotype_fraction:
              valueFrom: $(inputs.delly_params.min_genotype_fraction)
            min_fraction_alt_support:
              valueFrom: $(inputs.delly_params.min_fraction_alt_support)
            min_sv_size:
              valueFrom: $(inputs.delly_params.min_sv_size)
            passing_filter_sites:
              valueFrom: $(inputs.delly_params.passing_filter_sites)

            output_filename:
              valueFrom: $(inputs.input_bcf.basename.replace('.bcf', '.pass.bcf'))
          out: [sv_file]

  #########################
  # Merge unfiltered bcfs #
  #########################

  merge_with_bcftools_unfiltered:
    in:
      tumor_sample_name: tumor_sample_name
      normal_sample_name: normal_sample_name
      bcf_files: call_sv_by_delly/delly_sv
      output_filename:
        valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.svs.vcf')

    out: [merged_file_unfiltered]

    run:
      class: CommandLineTool
      baseCommand: [bcftools, concat, -a]
      stdout: $(inputs.output_filename)

      inputs:

        bcf_files:
          type:
            type: array
            items: File
          secondaryFiles:
            - ^.bcf.csi
          inputBinding:
            position: 2

        output_filename:
          type: string
          inputBinding:
            prefix: --output
            position: 1

      outputs:
        merged_file_unfiltered:
          type: stdout

  #######################
  # Merge filtered bcfs #
  #######################

  merge_with_bcftools:
    in:
      tumor_sample_name: tumor_sample_name
      normal_sample_name: normal_sample_name
      pass_bcf_files: call_sv_by_delly/delly_filtered_sv
      output_filename:
        valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.svs.pass.vcf')

    out: [merged_file]

    run:
      class: CommandLineTool
      baseCommand: [bcftools, concat, -a]
      stdout: $(inputs.output_filename)

      inputs:
        pass_bcf_files:
          type: File[]
          secondaryFiles: [^.bcf.csi]
          inputBinding:
            position: 2

        output_filename:
          type: string
          inputBinding:
            prefix: --output
            position: 1

      outputs:
        merged_file:
          type: stdout

  vcf2maf:
    run: ../cwl_tools/vcf2maf/vcf2maf.cwl
    in:
      vcf2maf_params: vcf2maf_params
      input_vcf: merge_with_bcftools/merged_file
      tmp_dir: tmp_dir
      vep_data: vep_data
      normal_id: normal_sample_name
      tumor_id: tumor_sample_name
      # Todo: Ask Allan what these are for:
      vcf_normal_id: normal_sample_name
      vcf_tumor_id: tumor_sample_name

      ref_fasta: reference_fasta
      filter_vcf: exac_filter

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
        valueFrom: $(inputs.input_vcf.basename.replace('.vcf','_vep.maf'))
    out: [output]
