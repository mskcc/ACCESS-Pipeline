cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.perl)
- $(inputs.vcf2maf)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 8000
    coresMin: 2
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_params/schemas/vcf2maf.yaml
      - $import: ../../resources/run_tools/ACCESS_variants_run_tools.yaml

inputs:

  run_tools: ../../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools
  perl: string
  vcf2maf: string
  vcf2maf_params: ../../resources/run_params/schemas/vcf2maf.yaml#vcf2maf_params

  input_vcf:
    type:
    - string
    - File
    doc: Path to input file in VCF format
    inputBinding:
      prefix: --input-vcf

  vcf_tumor_id:
    type: string?
    doc: Tumor sample ID used in VCF's genotype columns
    inputBinding:
      prefix: --vcf-tumor-id

  tumor_id:
    type: string?
    doc: Tumor_Sample_Barcode to report in the MAF
    inputBinding:
      prefix: --tumor-id

  vcf_normal_id:
    type: string?
    doc: Matched normal ID used in VCF's genotype columns
    inputBinding:
      prefix: --vcf-normal-id

  normal_id:
    type: string?
    doc: Matched_Norm_Sample_Barcode to report in the MAF
    inputBinding:
      prefix: --normal-id

  species:
    type:
    - 'null'
    - type: enum
      symbols: [homo_sapiens, mus_musculus]
    default: homo_sapiens
    doc: Species of variants in input
    inputBinding:
      prefix: --species

  ncbi_build:
    type:
    - 'null'
    - type: enum
      symbols: [GRCh37, GRCh38, GRCm38]
    default: GRCh37
    doc: Genome build of variants in input
    inputBinding:
      prefix: --ncbi-build

  ref_fasta:
    type: File
    doc: Reference FASTA file
    inputBinding:
      prefix: --ref-fasta

  maf_center:
    type: string
    doc: Variant calling center to report in MAF
    inputBinding:
      prefix: --maf-center

  output_maf:
    type: string
    doc: Path to output MAF file
    inputBinding:
      prefix: --output-maf

  vep_path:
    type: string
    doc: Folder containing variant_effect_predictor.pl
    inputBinding:
      prefix: --vep-path

  vep_data:
    type: string
    doc: VEP's base cache/plugin directory
    inputBinding:
      prefix: --vep-data

  max_filter_ac:
    type: int
    doc: Use tag common_variant if the filter-vcf reports a subpopulation AC higher
      than this
    inputBinding:
      prefix: --max-filter-ac

  min_hom_vaf:
    type: float
    doc: If GT undefined in VCF, minimum allele fraction to call a variant homozygous
    inputBinding:
      prefix: --min-hom-vaf

  buffer_size:
    type: int
    doc: Number of variants VEP loads at a time; Reduce this for low memory systems
    inputBinding:
      prefix: --buffer-size

  custom_enst:
    type: string
    doc: List of custom ENST IDs that override canonical selection
    inputBinding:
      prefix: --custom-enst

  tmp_dir:
    type: Directory
    doc: Folder to retain intermediate VCFs after runtime
    inputBinding:
      prefix: --tmp-dir

  vep_forks:
    type: int
    doc: Number of forked processes to use when running VEP
    inputBinding:
      prefix: --vep-forks

  filter_vcf:
    type: File
    doc: The non-TCGA VCF from exac.broadinstitute.org
    inputBinding:
      prefix: --filter-vcf
    secondaryFiles:
    - .tbi

  retain_info:
    type: string
    doc: Comma-delimited names of INFO fields to retain as extra columns in MAF
    inputBinding:
      prefix: --retain-info

  remap_chain:
    type: string?
    doc: Chain file to remap variants to a different assembly before running VEP
    inputBinding:
      prefix: --remap-chain

  any_allele:
    type: string?
    doc: When reporting co-located variants, allow mismatched variant alleles too
    inputBinding:
      prefix: --any-allele

outputs:

  output:
    type: File
    outputBinding:
      glob: $(inputs.output_maf)
