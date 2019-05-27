cwlVersion: cwl:v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 16000
    coresMin: 2
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_params/schemas/basic-filtering-mutect.yaml

doc: |
  Filter snps from the output of muTect

baseCommand: filter_mutect

inputs:

  basicfiltering_mutect_params: ../../resources/run_params/schemas/basic-filtering-mutect.yaml#basicfiltering_mutect_params

  verbose:
    type: ['null', boolean]
    default: false
    doc: More verbose logging to help with debugging
    inputBinding:
      prefix: --verbose

  inputVcf:
    type:
    - string
    - File
    doc: Input vcf muTect file which needs to be filtered
    inputBinding:
      prefix: --inputVcf

  inputTxt:
    type:
    - string
    - File
    doc: Input txt muTect file which needs to be filtered
    inputBinding:
      prefix: --inputTxt

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
    secondaryFiles: ["^.tbi", ".tbi"]
    outputBinding:
      glob: |
        ${
          if (inputs.inputVcf)
            return inputs.inputVcf.basename.replace(".vcf","_STDfilter.norm.vcf.gz");
          return null;
        }

  txt:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.inputTxt)
            return inputs.inputTxt.basename.replace(".txt","_STDfilter.txt");
          return null;
        }
