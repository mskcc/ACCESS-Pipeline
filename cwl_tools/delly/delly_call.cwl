cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 7000
    coresMin: 2

baseCommand: [/opt/common/CentOS_6-dev/delly/0.7.7/delly, call]

inputs:

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
    type: boolean
#    default: false
    doc: include regions marked in this genome
    inputBinding:
      prefix: --all_regions

  sv_type:
    type: string
#    default: DEL
    doc: SV type (DEL, DUP, INV, BND, INS)
    inputBinding:
      prefix: --type

  reference_fasta:
    # Todo: make File
    type: string
    doc: genome fasta file
    inputBinding:
      prefix: --genome

  excluded_regions:
    type: string?
    doc: file with regions to exclude
    inputBinding:
      prefix: --exclude_file

  output_filename:
    type: string?
#    default: sv.bcf
    doc: SV BCF output file
    inputBinding:
      prefix: --outfile

  min_paired_end_mapping_quality:
    type: int?
#    default: 1
    doc: min. paired-end mapping quality
    inputBinding:
      prefix: --map-qual

  insert_size_cutoff:
    type: int?
#    default: 9
    doc: insert size cutoff, median+s*MAD (deletions only)
    inputBinding:
      prefix: --mad-cutoff

  no_small_indels:
    type: boolean?
#    default: false
    doc: no small InDel calling
    inputBinding:
      prefix: --noindels

  vcf_input:
    type: string?
#    doc: input VCF/BCF file for re-genotyping
    inputBinding:
      prefix: --vcffile

  min_genotyping_map_quality:
    type: int?
#    default: 5
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
      glob: |
        ${
          if (inputs.o)
            return inputs.o;
          return null;
        }
