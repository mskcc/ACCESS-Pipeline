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
      - $import: ../../resources/run_params/schemas/mutect.yaml
      - $import: ../../resources/run_params/schemas/vardict.yaml

inputs:

  tmp_dir: Directory
  mutect_params: ../../resources/run_params/schemas/mutect.yaml#mutect_params
  vardict_params: ../../resources/run_params/schemas/vardict.yaml#vardict_params

  tumor_bam:
    type: File
    secondaryFiles: [^.bai]
  normal_bam:
    type: File
    secondaryFiles: [^.bai]
  tumor_sample_name: string
  normal_sample_name: string
  dbsnp:
    type: File
    secondaryFiles: [.idx]
  cosmic:
    type: File
    secondaryFiles: [.idx]
  bed_file: File
  refseq: File
  hotspot_vcf: File
  ref_fasta: File

outputs:

  mutect_vcf:
    type: File
    outputSource: mutect/output

  mutect_callstats:
    type: File
    outputSource: mutect/callstats_output

  vardict_vcf:
    type: File
    outputSource: vardict/output

steps:
  vardict:
    run: ../../cwl_tools/vardict/vardict_paired.cwl
    in:
      vardict_params: vardict_params
      G: ref_fasta
      b: tumor_bam
      b2: normal_bam
      N: tumor_sample_name
      N2: normal_sample_name
      bed_file: bed_file
      E:
        valueFrom: $(inputs.vardict_params.E)
      S:
        valueFrom: $(inputs.vardict_params.S)
      c:
        valueFrom: $(inputs.vardict_params.c)
      g:
        valueFrom: $(inputs.vardict_params.g)
      f:
        valueFrom: $(inputs.vardict_params.f)
      r:
        valueFrom: $(inputs.vardict_params.r)
      output_file_name:
        valueFrom: $(inputs.N + '.' + inputs.N2 + '.vardict.vcf')
    out: [output]

  mutect:
    run: ../../cwl_tools/mutect/mutect.cwl
    in:
      tmp_dir: tmp_dir
      mutect_params: mutect_params
      input_file_normal: normal_bam
      input_file_tumor: tumor_bam
      tumor_sample_name: tumor_sample_name
      normal_sample_name: normal_sample_name
      reference_sequence: ref_fasta
      dbsnp: dbsnp
      cosmic: cosmic
      intervals: bed_file
      read_filter:
        valueFrom: $(inputs.mutect_params.rf)
      downsample_to_coverage:
        valueFrom: $(inputs.mutect_params.dcov)
      fraction_contamination:
        valueFrom: $(inputs.mutect_params.fraction_contamination)
      minimum_mutation_cell_fraction:
        valueFrom: $(inputs.mutect_params.minimum_mutation_cell_fraction)
      vcf:
        valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.mutect.vcf')
      out:
        valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.mutect.txt')
    out: [output, callstats_output]
