cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java_8)
# todo: why server?
- -server
- -Xms4g
- -Xmx4g
- -cp
- $(inputs.waltz_path)
- org.mskcc.juber.waltz.Waltz
- PileupMetrics

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 16000
    coresMin: 1
    outdirMax: 30000

inputs:

  java_8: string
  waltz_path: string

  min_mapping_quality:
    type: int
    inputBinding:
      position: 1

  input_bam:
    type: File
    secondaryFiles: [^.bai]
    inputBinding:
      position: 2

  reference_fasta:
    type: string
    inputBinding:
      position: 3
    secondaryFiles: $(inputs.reference_fasta.path + '.fai')

  bed_file:
    type: File
    inputBinding:
      position: 4

outputs:

  pileup:
    type: File
    outputBinding:
      glob: '*-pileup.txt'

  pileup_without_duplicates:
    type: File
    outputBinding:
      glob: '*-pileup-without-duplicates.txt'

  intervals:
    type: File
    outputBinding:
      glob: '*-intervals.txt'

  intervals_without_duplicates:
    type: File
    outputBinding:
      glob: '*-intervals-without-duplicates.txt'
