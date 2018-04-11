#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_31/bin/java

arguments:
# todo: why server?
- -server
- -Xms4g
- -Xmx4g
- -cp
- /home/johnsoni/Innovation-Pipeline/vendor_tools/Waltz-2.0.jar
- org.mskcc.juber.waltz.countreads.CountReads

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 8000
    coresMin: 1

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