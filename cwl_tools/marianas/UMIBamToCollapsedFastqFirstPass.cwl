cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java_8)
- -server
- -Xms8g
- -Xmx8g
- -cp
- $(inputs.marianas_path)
- org.mskcc.marianas.umi.duplex.DuplexUMIBamToCollapsedFastqFirstPass

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 1
    outdirMax: 30000

inputs:

  java_8: string
  marianas_path: string

  input_bam:
    type: File
    inputBinding:
      position: 1

  pileup:
    type: File
    inputBinding:
      position: 2

  min_mapping_quality:
    type: int
    inputBinding:
      position: 3

  min_base_quality:
    type: int
    inputBinding:
      position: 4

  mismatches:
    type: int
    inputBinding:
      position: 5

  wobble:
    type: int
    inputBinding:
      position: 6

  min_consensus_percent:
    type: int
    inputBinding:
      position: 7

  reference_fasta:
    type: string
    inputBinding:
      position: 8

  reference_fasta_fai: string

  output_dir:
    type: ['null', string]
    default: '.'
    inputBinding:
      position: 9
      valueFrom: '.'

outputs:

  first_pass_output_file:
    type: File
    outputBinding:
      glob: ${return 'first-pass.txt'}

  alt_allele_file:
    type: File
    outputBinding:
      glob: ${return 'first-pass-alt-alleles.txt'}

  first_pass_insertions:
    type: File
    outputBinding:
      glob: ${return 'first-pass-insertions.txt'}

  first_pass_output_dir:
    type: Directory
    outputBinding:
      glob: '.'
