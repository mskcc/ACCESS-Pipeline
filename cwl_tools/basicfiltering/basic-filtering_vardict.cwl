cwlVersion: v1.0

class: CommandLineTool

requirements:
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/params/basic-filtering-vardict.yaml
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 10000
    coresMin: 2

doc: |
  Filter snps/indels from the output of vardict

baseCommand: filter_vardict

inputs:

  basicfiltering_vardict_params: ../../resources/schemas/params/basic-filtering-vardict.yaml#basicfiltering_vardict_params

  filter_germline:
    type: boolean
    inputBinding:
      prefix: --filter_germline

  verbose:
    type: boolean?
    default: false
    doc: More verbose logging to help with debugging
    inputBinding:
      prefix: --verbose

  inputVcf:
    type:
    - string
    - File
    doc: Input vcf vardict file which needs to be filtered
    inputBinding:
      prefix: --inputVcf

  tsampleName:
    type: string
    doc: Name of the tumor Sample
    inputBinding:
      prefix: --tsampleName

  refFasta:
    type:
    - string
    - File
    doc: Reference genome in fasta format
    inputBinding:
      prefix: --refFasta

  total_depth:
    type: int
    doc: Tumor total depth threshold
    inputBinding:
      prefix: --totaldepth

  allele_depth:
    type: int
    doc: Tumor allele depth threshold
    inputBinding:
      prefix: --alleledepth

  tumor_normal_ratio:
    type: int
    doc: Tumor-Normal variant frequency ratio threshold
    inputBinding:
      prefix: --tnRatio

  variant_fraction:
    type: float
    doc: Tumor variant frequency threshold
    inputBinding:
      prefix: --variantfraction

  min_qual:
    type: int
    doc: Minimum variant call quality
    inputBinding:
      prefix: --minqual

  hotspotVcf:
    type:
    - 'null'
    - string
    - File
    doc: Input vcf file with hotspots that skip VAF ratio filter
    inputBinding:
      prefix: --hotspotVcf

  outdir:
    type: ['null', string]
    doc: Full Path to the output dir.
    inputBinding:
      prefix: --outDir

outputs:

  vcf:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.inputVcf)
            return inputs.inputVcf.basename.replace(".vcf","_STDfilter.norm.vcf.gz");
          return null;
        }
    secondaryFiles: ['^.tbi', '.tbi']

  txt:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.inputVcf)
            return inputs.inputVcf.basename.replace(".vcf","_STDfilter.txt");
          return null;
        }