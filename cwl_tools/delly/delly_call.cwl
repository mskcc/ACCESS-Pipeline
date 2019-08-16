cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_params/schemas/delly.yaml
  ResourceRequirement:
    ramMin: 7000
    coresMin: 2

baseCommand: [/opt/common/CentOS_6-dev/delly/0.7.7/delly, call]

inputs:

  delly_params: ../../resources/run_params/schemas/delly.yaml#delly_params

  tumor_bam:
    type: File
    doc: Sorted tumor bam
    inputBinding:
      position: 999
    secondaryFiles: [^.bai]

  normal_bam:
    type: File
    doc: Sorted normal bam
    inputBinding:
      position: 1000
    secondaryFiles: [^.bai]

  all_regions:
    type: boolean?
    doc: include regions marked in this genome
    inputBinding:
      prefix: --all_regions

  sv_type:
    type: string
    doc: SV type (DEL, DUP, INV, BND, INS)
    inputBinding:
      prefix: --type

  reference_fasta:
    type: File
    doc: genome fasta file
    inputBinding:
      prefix: --genome

  excluded_regions:
    type: File?
    doc: file with regions to exclude
    inputBinding:
      prefix: --exclude

  output_filename:
    type: string
    doc: SV BCF output file
    inputBinding:
      prefix: --outfile

  min_paired_end_mapping_quality:
    type: int?
    doc: min. paired-end mapping quality
    inputBinding:
      prefix: --map-qual

  insert_size_cutoff:
    type: int?
    doc: insert size cutoff, median+s*MAD (deletions only)
    inputBinding:
      prefix: --mad-cutoff

  no_small_indels:
    type: boolean?
    doc: no small InDel calling
    inputBinding:
      prefix: --noindels

  vcf_input:
    type: string?
    doc: input VCF/BCF file for re-genotyping
    inputBinding:
      prefix: --vcffile

  min_genotyping_map_quality:
    type: int?
    doc: min. mapping quality for genotyping
    inputBinding:
      prefix: --geno-qual

  stderr:
    type: string?
    doc: log stderr to file
    inputBinding:
      prefix: --stderr

  stdout:
    type: string?
    doc: log stdout to file
    inputBinding:
      prefix: --stdout

outputs:

  sv_file:
    type: File
    secondaryFiles:
      - ^.bcf.csi
    outputBinding:
      glob: $(inputs.output_filename)