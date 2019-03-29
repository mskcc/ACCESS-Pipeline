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
- org.mskcc.juber.waltz.countreads.CountReads

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1
    outdirMax: 30000

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      position: 1

  coverage_threshold:
    type: int
    inputBinding:
      position: 2

  gene_list:
    type: File
    inputBinding:
      position: 3

  bed_file:
    type: File
    inputBinding:
      position: 4

outputs:
  # Todo: We should be able to use "glob: ." and then skip the group_waltz_files step
  covered_regions:
    type: File
    outputBinding:
      glob: '*.covered-regions'

  fragment_sizes:
    type: File
    outputBinding:
      glob: '*.fragment-sizes'

  read_counts:
    type: File
    outputBinding:
      glob: '*.read-counts'