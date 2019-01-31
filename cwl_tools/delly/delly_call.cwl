cwlVersion: cwl:v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 7
    coresMin: 2

baseCommand:
- cmo_delly
- --version
- 0.7.7
- --cmd
- call

inputs:
  t:
    type: ['null', string]
    default: DEL
    doc: SV type (DEL, DUP, INV, BND, INS)
    inputBinding:
      prefix: --type

  reference_fasta:
    # Todo: make File
    type: string
    doc: genome fasta file
    inputBinding:
      prefix: --genome

  x:
    type: ['null', string]
    doc: file with regions to exclude
    inputBinding:
      prefix: --exclude_file

  o:
    type: ['null', string]
    default: sv.bcf
    doc: SV BCF output file
    inputBinding:
      prefix: --outfile

  q:
    type: ['null', int]
    default: 1
    doc: min. paired-end mapping quality
    inputBinding:
      prefix: --map-qual

  s:
    type: ['null', int]
    default: 9
    doc: insert size cutoff, median+s*MAD (deletions only)
    inputBinding:
      prefix: --mad-cutoff

  n:
    type: ['null', boolean]
    default: false
    doc: no small InDel calling
    inputBinding:
      prefix: --noindels

  v:
    type: ['null', string]
    doc: input VCF/BCF file for re-genotyping
    inputBinding:
      prefix: --vcffile

  u:
    type: ['null', int]
    default: 5
    doc: min. mapping quality for genotyping
    inputBinding:
      prefix: --geno-qual

  normal_bam:
    type: File
    doc: Sorted normal bam
    inputBinding:
      prefix: --normal_bam
    secondaryFiles: [.bai]
  tumor_bam:
    type: File
    doc: Sorted tumor bam
    inputBinding:
      prefix: --tumor_bam
    secondaryFiles: [.bai]
  all_regions:
    type: ['null', boolean]
    default: false
    doc: include regions marked in this genome
    inputBinding:
      prefix: --all_regions

  stderr:
    type: ['null', string]
    doc: log stderr to file
    inputBinding:
      prefix: --stderr

  stdout:
    type: ['null', string]
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
