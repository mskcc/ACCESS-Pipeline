cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ShellCommandRequirement: {}
  ResourceRequirement:
    ramMin: 40000
    coresMin: 2
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/params/gbcms_params.yaml
      - $import: ../../resources/schemas/variants_tools.yaml

arguments:
- $(inputs.gbcms)
- shellQuote: false
  valueFrom: |
    ${
      return inputs.Traceback_ids.map(function(b, i) {
        return '--bam ' + b + ':' + inputs.Traceback_bam_files[i].path
      }).join(' ')
    }

inputs:

  #run_tools: ../../resources/run_tools/ACCESS_variants_run_tools.yaml#run_tools
  #gbcms_params: ../../resources/run_params/schemas/gbcms_params.yaml#gbcms_params
  gbcms: string

  Traceback_ids: string[]
  Traceback_bam_files:
    type: File[]
    secondaryFiles:
      - ^.bai

  traceback_inputs_maf:
    type: File
    doc: MAF file on which to fillout
    inputBinding:
      prefix: --maf

  ref_fasta:
    type: File
    secondaryFiles: [.fai]
    inputBinding:
      prefix: --fasta

  output:
    type: string?
    doc: Filename for output of raw fillout data in MAF/VCF format
    inputBinding:
      prefix: --output

  omaf:
    type: boolean
    inputBinding:
      prefix: --omaf

  filter_duplicate:
    type: int
    inputBinding:
      prefix: --filter_duplicate

  thread:
    type: int
    inputBinding:
      prefix: --thread

  maq:
    type: int
    inputBinding:
      prefix: --maq

  fragment_count:
    type: int
    inputBinding:
      prefix: --fragment_count

outputs:

  tb_fillout_out:
    type: File
    outputBinding:
      glob: traceback_out.maf
