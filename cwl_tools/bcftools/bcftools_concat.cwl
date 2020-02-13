cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.bcftools)
- concat

#stdout: $(inputs.output)

requirements:
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/variants_tools.yaml
      - $import: ../../resources/schemas/params/bcftools.yaml
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1

doc: |
  concatenate VCF/BCF files from the same set of samples

inputs:

  bcftools: string
  run_tools: ../../resources/schemas/variants_tools.yaml#run_tools
  bcftools_params: ../../resources/schemas/params/bcftools.yaml#bcftools_params

  tumor_sample_name: string
  normal_sample_name: string
 
  threads:
    type: string?
    doc: Number of extra output compression threads [0]
    inputBinding:
      prefix: --threads 

  compact_PS:
    type: boolean?
    default: false
    doc: Do not output PS tag at each site, only at the start of a new phase set block.
    inputBinding:
      prefix: --compact-PS 

  remove_duplicates:
    type: boolean?
    default: false
    doc: Alias for -d none
    inputBinding:
      prefix: --remove-duplicates 

  ligate:
    type: boolean?
    default: false
    doc: Ligate phased VCFs by matching phase at overlapping haplotypes
    inputBinding:
      prefix: --ligate 

  output_type:
    type: string?
    doc: <b|u|z|v> b - compressed BCF, u - uncompressed BCF, z - compressed VCF, v - uncompressed VCF [v]
    inputBinding:
      prefix: --output-type 

  no_version:
    type: boolean?
    default: false
    doc: do not append version and command line to the header
    inputBinding:
      prefix: --no-version 

  naive:
    type: boolean?
    default: false
    doc: Concatenate BCF files without recompression (dangerous, use with caution)
    inputBinding:
      prefix: --naive 

  allow_overlaps:
    type: boolean?
    default: false
    doc: First coordinate of the next file can precede last record of the current file.
    inputBinding:
      prefix: --allow-overlaps 

  min_PQ:
    type: string?
    doc: Break phase set if phasing quality is lower than <int> [30]
    inputBinding:
      prefix: --min-PQ 

  regions_file:
    type: string?
    doc: Restrict to regions listed in a file
    inputBinding:
      prefix: --regions-file 

  regions:
    type: string?
    doc: Restrict to comma-separated list of regions
    inputBinding:
      prefix: --regions 

  rm_dups:
    type: string?
    doc: Output duplicate records present in multiple files only once - <snps|indels|both|all|none>
    inputBinding:
      prefix: --rm-dups 

  output:
    type: string
    doc: Write output to a file [standard output]
    default: "bcftools_concat.vcf"
    inputBinding:
      prefix: --output

  list:
    type: string?
    doc: Read the list of files from a file.
    inputBinding:
      prefix: --file-list 

  vcf_files:
    type: File[]
    secondaryFiles: 
      - .tbi
    doc: Array of vcf files to be concatenated into one vcf
    inputBinding:
      position: 1

outputs:

  concat_vcf_output_file:
    type: File
    outputBinding:
      glob: ${return inputs.output;}
