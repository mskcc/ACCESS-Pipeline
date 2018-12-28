cwlVersion: cwl:v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ShellCommandRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_params/schemas/gbcms_params.yaml
  ResourceRequirement:
    ramMin: 32000
    coresMin: 2

# Todo items:
# - cmo_fillout has a section to create Portal fillout
# - cmo_fillout creates "a temporary MAF with events deduplicated by genomic loci and ref/alt alleles"
# - cmo_fillout has "Check if MAF has right genome"

baseCommand: /ifs/work/bergerm1/Innovation/software/maysun/GetBaseCountsMultiSample/GetBaseCountsMultiSample

arguments:
# Todo: try without shellQuote: false
- shellQuote: false
  valueFrom: |
    ${
      return inputs.genotyping_bams_ids.map(function(b, i) {
        return '--bam ' + b + ':' + inputs.genotyping_bams[i].path
      }).join(' ')
    }

inputs:

  gbcms_params: ../../resources/run_params/schemas/gbcms_params.yaml#gbcms_params

  genotyping_bams_ids: string[]
  genotyping_bams: File[]

  maf:
    type: File
    doc: MAF file on which to fillout
    inputBinding:
      prefix: --maf

  ref_fasta:
    type: File
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

  fillout_out:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.output)
            return inputs.output;
          else
            return inputs.maf.basename.replace(".maf", ".fillout");
        }
