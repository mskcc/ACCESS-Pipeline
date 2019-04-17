cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../resources/run_tools/schemas.yaml
      - $import: ../resources/run_params/schemas/trimgalore.yaml
      - $import: ../resources/run_params/schemas/add_or_replace_read_groups.yaml
      - $import: ../resources/run_params/schemas/mark_duplicates.yaml

inputs:
  run_tools: ../resources/run_tools/schemas.yaml#run_tools
  trimgalore__params: ../resources/run_params/schemas/trimgalore.yaml#trimgalore__params
  add_or_replace_read_groups__params: ../resources/run_params/schemas/add_or_replace_read_groups.yaml#add_or_replace_read_groups__params
  mark_duplicates__params: ../resources/run_params/schemas/mark_duplicates.yaml#mark_duplicates__params

  reference_fasta: string
  reference_fasta_fai: string

  fastq1: File
  fastq2: File
  adapter: string
  adapter2: string
  add_rg_LB: int
  add_rg_PL: string
  add_rg_ID: string
  add_rg_PU: string
  add_rg_SM: string
  add_rg_CN: string

outputs:

  clstats1:
    type: File
    outputSource: trimgalore/clstats1

  clstats2:
    type: File
    outputSource: trimgalore/clstats2

  bam:
    type: File
    outputSource: picard.MarkDuplicates/bam

  # Todo: unnecessary output
  bai:
    type: File
    outputSource: picard.MarkDuplicates/bai

  md_metrics:
    type: File
    outputSource: picard.MarkDuplicates/mdmetrics

steps:

  trimgalore:
    run: ../cwl_tools/trimgalore/trimgalore.cwl
    in:
      run_tools: run_tools
      params: trimgalore__params
      perl:
        valueFrom: $(inputs.run_tools.perl_5)
      trimgalore:
        valueFrom: $(inputs.run_tools.trimgalore_path)

      fastq1: fastq1
      fastq2: fastq2
      adapter: adapter
      adapter2: adapter2
      length:
        valueFrom: $(inputs.params.length)
      paired:
        valueFrom: $(inputs.params.paired)
      gzip:
        valueFrom: $(inputs.params.gzip)
      quality:
        valueFrom: $(inputs.params.quality)
      stringency:
        valueFrom: $(inputs.params.stringency)
      suppress_warn:
        valueFrom: $(inputs.params.suppress_warn)
    out: [clfastq1, clfastq2, clstats1, clstats2]

  bwa_mem:
    run: ../cwl_tools/bwa-mem/bwa-mem.cwl
    in:
      run_tools: run_tools
      bwa:
        valueFrom: $(inputs.run_tools.bwa_path)

      fastq1: trimgalore/clfastq1
      fastq2: trimgalore/clfastq2
      reference_fasta: reference_fasta
      reference_fasta_fai: reference_fasta_fai
      ID: add_rg_ID
      LB: add_rg_LB
      SM: add_rg_SM
      PL: add_rg_PL
      PU: add_rg_PU
      CN: add_rg_CN
    out: [output_sam]

  picard.AddOrReplaceReadGroups:
    run: ../cwl_tools/picard/AddOrReplaceReadGroups.cwl
    in:
      run_tools: run_tools
      params: add_or_replace_read_groups__params
      java:
        valueFrom: $(inputs.run_tools.java_7)
      arrg:
        valueFrom: $(inputs.run_tools.arrg_path)

      input_sam: bwa_mem/output_sam
      LB: add_rg_LB
      PL: add_rg_PL
      ID: add_rg_ID
      PU: add_rg_PU
      SM: add_rg_SM
      CN: add_rg_CN
      sort_order:
        valueFrom: $(inputs.params.sort_order)
      validation_stringency:
        valueFrom: $(inputs.params.validation_stringency)
      compression_level:
        valueFrom: $(inputs.params.compression_level)
      create_index:
        valueFrom: $(inputs.params.create_index)
    out: [bam, bai]

  picard.MarkDuplicates:
    run: ../cwl_tools/picard/MarkDuplicates.cwl
    in:
      run_tools: run_tools
      params: mark_duplicates__params
      java:
        valueFrom: $(inputs.run_tools.java_8)
      picard:
        valueFrom: $(inputs.run_tools.picard_path)
      input_bam: picard.AddOrReplaceReadGroups/bam

      assume_sorted:
        valueFrom: $(inputs.params.assume_sorted)
      compression_level:
        valueFrom: $(inputs.params.compression_level)
      create_index:
        valueFrom: $(inputs.params.create_index)
      validation_stringency:
        valueFrom: $(inputs.params.validation_stringency)
      duplicate_scoring_strategy:
        valueFrom: $(inputs.params.duplicate_scoring_strategy)
    out: [bam, bai, mdmetrics]
