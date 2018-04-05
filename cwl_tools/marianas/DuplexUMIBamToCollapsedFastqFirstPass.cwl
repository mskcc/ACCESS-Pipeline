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
- /home/johnsoni/Innovation-Pipeline/vendor_tools/Marianas-true-duplex-1-1.jar
- org.mskcc.marianas.umi.duplex.DuplexUMIBamToCollapsedFastqFirstPass

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
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

  output_dir:
    type: ['null', string]
    inputBinding:
      position: 7

outputs:

  first_pass_output_file:
    type: File
    outputBinding:
      glob: ${ return "first-pass.txt" }

  alt_allele_file:
    type: File
    outputBinding:
      glob: ${ return 'first-pass-alt-alleles.txt' }

  first_pass_output_dir:
    type: Directory
    outputBinding:
      glob: '.'