cwlVersion: v1.0

class: CommandLineTool

baseCommand:
- cmo_delly
- --version
- 0.7.7
- --cmd
- merge

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 7
    coresMin: 2

doc: |
  None

inputs:
  t:
    type: ['null', string]
    default: DEL
    doc: SV type (DEL, DUP, INV, BND, INS)
    inputBinding:
      prefix: --type

  o:
    type: ['null', string]
    default: sv.bcf
    doc: Merged SV BCF output file
    inputBinding:
      prefix: --outfile

  m:
    type: ['null', int]
    default: 0
    doc: min. SV size
    inputBinding:
      prefix: --minsize

  n:
    type: ['null', int]
    default: 1000000
    doc: max. SV size
    inputBinding:
      prefix: --maxsize

  c:
    type: ['null', boolean]
    default: false
    doc: Filter sites for PRECISE
    inputBinding:
      prefix: --precise

  p:
    type: ['null', boolean]
    default: false
    doc: Filter sites for PASS
    inputBinding:
      prefix: --pass

  b:
    type: ['null', int]
    default: 1000
    doc: max. breakpoint offset
    inputBinding:
      prefix: --bp-offset

  r:
    type: ['null', float]
    default: 0.800000012
    doc: min. reciprocal overlap
    inputBinding:
      prefix: --rec-overlap

  i:
    type:
      type: array
      items: File
    inputBinding:
      prefix: --input
      itemSeparator: ' '
      separate: true
    doc: Input files (.bcf)
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
    outputBinding:
      glob: |
        ${
          if (inputs.o)
            return inputs.o;
          return null;
        }
