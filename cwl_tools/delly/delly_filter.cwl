cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 7000
    coresMin: 2

baseCommand: [/opt/common/CentOS_6-dev/delly/0.7.7/delly, filter]

inputs:

  input_bcf:
    type: File
    doc: Input file (.bcf)
    inputBinding:
      # Todo:
      position: 999

  sv_type:
    type: string?
#    default: DEL
    doc: SV type (DEL, DUP, INV, BND, INS)
    inputBinding:
      prefix: --type

  filter_mode:
    type: string?
#    default: somatic
    doc: Filter mode (somatic, germline)
    inputBinding:
      prefix: --filter

  output_filename:
    type: string?
#    default: sv.bcf
    doc: Filtered SV BCF output file
    inputBinding:
      prefix: --outfile

  min_fraction_alt_support:
    type: float?
#    default: 0.1
    doc: min. fractional ALT support
    inputBinding:
      prefix: --altaf

  min_sv_size:
    type: int?
#    default: 500
    doc: min. SV size
    inputBinding:
      prefix: --minsize

  max_sv_size:
    type: ['null', int]
#    default: 500000000
    doc: max. SV size
    inputBinding:
      prefix: --maxsize

  min_genotype_fraction:
    type: ['null', float]
#    default: 0.0
    doc: min. fraction of genotyped samples
    inputBinding:
      prefix: --ratiogeno

  passing_filter_sites:
    type: ['null', boolean]
#    default: true
    doc: Filter sites for PASS
    inputBinding:
      prefix: --pass

  sample_file:
    type: File
    doc: Two-column sample file listing sample name and tumor or control
    inputBinding:
      prefix: --samples

  min_coverage_in_tumor:
    type: int?
#    default: 10
    doc: min. coverage in tumor
    inputBinding:
      prefix: --coverage

  max_fractional_alt_support:
    type: int?
#    default: 0
    doc: max. fractional ALT support in control
    inputBinding:
      prefix: --controlcontamination

  min_median_gq:
    type: int?
#    default: 15
    doc: min. median GQ for carriers and non-carriers
    inputBinding:
      prefix: --gq

  max_read_depth_ratio:
    type: float
#    default: 0.800000012
    doc: max. read-depth ratio of carrier vs. non-carrier for a deletion
    inputBinding:
      prefix: --rddel

  min_read_depth_ratio:
    type: float?
#    default: 1.20000005
    doc: min. read-depth ratio of carrier vs. non-carrier for a duplication
    inputBinding:
      prefix: --rddup

  all_regions:
    type: boolean?
#    default: false
    doc: include regions marked in this genome
    inputBinding:
      prefix: --all_regions

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
      glob: |
        ${
          if (inputs.o)
            return inputs.o;
          return null;
        }
