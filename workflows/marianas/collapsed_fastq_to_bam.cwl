cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SubworkflowFeatureRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/collapsing_tools.yaml
      - $import: ../../resources/schemas/params/marianas_collapsing.yaml
      - $import: ../../resources/schemas/params/add_or_replace_read_groups.yaml

inputs:
  run_tools: ../../resources/schemas/collapsing_tools.yaml#run_tools
  add_or_replace_read_groups__params: ../../resources/schemas/params/add_or_replace_read_groups.yaml#add_or_replace_read_groups__params

  fastq1: File
  fastq2: File
  reference_fasta: string
  reference_fasta_fai: string
  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string

outputs:

  bam:
    type: File
    outputSource: add_or_replace_read_groups/bam

  bai:
    type: File
    outputSource: add_or_replace_read_groups/bai

steps:

  bwa_mem:
    run: ../../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      run_tools: run_tools
      bwa:
        valueFrom: ${return inputs.run_tools.bwa_path}

      fastq1: fastq1
      fastq2: fastq2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      ID: add_rg_ID
      LB: add_rg_LB
      SM: add_rg_SM
      PL: add_rg_PL
      PU: add_rg_PU
      CN: add_rg_CN
    out: [output_sam]

  add_or_replace_read_groups:
    run: ../../cwl_tools/picard/AddOrReplaceReadGroups.cwl
    in:
      run_tools: run_tools
      add_or_replace_read_groups__params: add_or_replace_read_groups__params
      java:
        valueFrom: ${return inputs.run_tools.java_7}
      arrg:
        valueFrom: ${return inputs.run_tools.arrg_path}

      input_sam: bwa_mem/output_sam
      LB: add_rg_LB
      PL: add_rg_PL
      ID: add_rg_ID
      PU: add_rg_PU
      SM: add_rg_SM
      CN: add_rg_CN
      sort_order:
        valueFrom: $(inputs.add_or_replace_read_groups__params.sort_order)
      validation_stringency:
        valueFrom: $(inputs.add_or_replace_read_groups__params.validation_stringency)
      compression_level:
        valueFrom: $(inputs.add_or_replace_read_groups__params.compression_level)
      create_index:
        valueFrom: $(inputs.add_or_replace_read_groups__params.create_index)
    out: [bam, bai]
