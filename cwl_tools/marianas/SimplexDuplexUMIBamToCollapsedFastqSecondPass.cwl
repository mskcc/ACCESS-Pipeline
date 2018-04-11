#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_31/bin/java

arguments:
- -server
- -Xms8g
- -Xmx8g
- -cp
- /home/johnsoni/Innovation-Pipeline/vendor_tools/Marianas-standard.jar
- org.mskcc.marianas.umi.duplex.DuplexUMIBamToCollapsedFastqSecondPass

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.first_pass_file)
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 1

doc: |
  None

inputs:
  input_bam:
    type: File
    inputBinding:
      position: 1

  pileup:
    type: File
    inputBinding:
      position: 2

  mismatches:
    type: int
    inputBinding:
      position: 3

  wobble:
    type: int
    inputBinding:
      position: 4

  min_consensus_percent:
    type: int
    inputBinding:
      position: 5

  reference_fasta:
    type: string
    inputBinding:
      position: 6

  reference_fasta_fai: string

  first_pass_file:
    type: File

  output_dir:
    type: ['null', string]
    default: '.'
    inputBinding:
      position: 7
      valueFrom: '.'

outputs:

  collapsed_fastq_1:
    type: File
    outputBinding:
      # Todo: This filename will become ..._cl_aln_srt_MD_IR_FX_BR__aln_srt.bam
      # Because the bwa step does not expect an extra underscore at the end
      # Would be nice if Marianas allowed specification of the output filename as an input paramter
      glob: ${ return 'collapsed_R1_.fastq' }

  collapsed_fastq_2:
    type: File
    outputBinding:
      glob: ${ return 'collapsed_R2_.fastq' }
