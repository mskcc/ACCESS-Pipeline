cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
#  SchemaDefRequirement:
#    types:
#      - $import: ../resources/run_params/schemas/vcf2maf.yaml

inputs:

#  vcf2maf_params: ../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params

  tumor_bam:
    type: File
    secondaryFiles: [^.bai]
  normal_bam:
    type: File
    secondaryFiles: [^.bai]

  normal_sample_name: string
  tumor_sample_name: string
#    genome: string
  delly_type: string[]
  vep_data: string
  reference_fasta: string

outputs:

  delly_sv:
    type:
      type: array
      items: File
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

  merged_file:
    type: File
    outputSource: merge_with_bcftools/merged_file

  merged_file_unfiltered:
    type: File
    outputSource: merge_with_bcftools_unfiltered/merged_file_unfiltered

#  maf_file:
#    type: File
#    outputSource: vcf2maf/output

#  portal_file:
#    type: File
#    outputSource: portal_format_output/portal_file

steps:

#  index:
#    run: cmo-index/1.0.0/cmo-index.cwl
#    in:
#      tumor: tumor_bam
#      normal: normal_bam
#    out: [tumor_bam, normal_bam]

  createTNPair:
    in:
      tumor_sample_name: tumor_sample_name
      normal_sample_name: normal_sample_name
      echoString:
        valueFrom: $(inputs.tumor_sample_name + "\ttumor\n" + inputs.normal_sample_name + "\tcontrol")
      output_filename:
        valueFrom: $(tn_pair.txt)
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
        tumor_bam: File
        normal_bam: File
        normal_sample_name: string
        tumor_sample_name: string
        delly_type: string
        pairfile: File
        reference_fasta: string

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
            sv_type: delly_type
            tumor_bam: tumor_bam
            normal_bam: normal_bam
            normal_sample_name: normal_sample_name
            tumor_sample_name: tumor_sample_name
            reference_fasta: reference_fasta
            output_filename:
              valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.' + inputs.t + '.bcf')
          out: [sv_file]

        delly_filter:
          run: ../cwl_tools/delly/delly_filter.cwl
          in:
            input_bcf: delly_call/sv_file
            sample_file: pairfile
            sv_type: delly_type
            output_filename:
              valueFrom: $(inputs.i.basename.replace('.bcf', '.pass.bcf'))
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

    merge_with_bcftools:
      in:
        tumor_sample_name: tumor_sample_name
        normal_sample_name: normal_sample_name
        pass_bcf_files: call_sv_by_delly/delly_filtered_sv
        output_filename:
          type: string
          inputBinding:
            prefix: --output
            position: 1

      outputs:
        merged_file:
          type: stdout

#  vcf2maf:
#    run: ../cwl_tools/vcf2maf/vcf2maf.cwl
#    in:
##        vcf2maf_params: vcf2maf_params
#      vep_data: vep_data
#      normal_id: normal_sample_name
#      tumor_id: tumor_sample_name
#      # Todo: Ask Allan what these are for:
#      vcf_normal_id: normal_sample_name
#      vcf_tumor_id: tumor_sample_name
#      input_vcf: merge_with_bcftools/merged_file
#      output_maf:
#        valueFrom: $(inputs.input_vcf.basename.replace('vcf','vep.maf'))
#    out: [output]

#    portal_format_output:
#      run: portal-formatting.cli/1.0.0/format-maf.cwl
#      in:
#        input_maf: convert_vcf2maf/output
#      out: [portal_file]
