cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java_8)
- -server
- -Xms8g
- -Xmx8g
- -cp
- $(inputs.marianas_path)
- org.mskcc.marianas.umi.duplex.DuplexUMIBamToCollapsedFastqSecondPass

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.first_pass_file)
  - class: ResourceRequirement
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

  first_pass_file:
    type: File

  output_dir:
    type: ['null', string]
    default: '.'
    inputBinding:
      position: 9
      valueFrom: '.'

outputs:

  collapsed_fastq_1:
    type: File
    outputBinding:
      # Todo: This filename will become ..._cl_aln_srt_MD_IR_FX_BR__aln_srt.bam
      # Because the bwa step does not expect an extra underscore at the end
      # Could possibly specify output filename as an input paramter
      glob: 'collapsed_R1_.fastq'

  collapsed_fastq_2:
    type: File
    outputBinding:
      glob: 'collapsed_R2_.fastq'

  second_pass_insertions:
    type: File
    outputBinding:
      glob: 'second-pass-insertions.txt'

  second_pass_alt_alleles:
    type: File
    outputBinding:
      glob: 'second-pass-alt-alleles.txt'
