#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
- -Xms8g
- -Xmx45g
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/fgbio-0.5.0.jar
- --tmp-dir=/scratch
- AnnotateBamWithUmis

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    # Requires large amount of ram (loads all read names into a java hashmap)
    ramMin: 50000
    coresMin: 1

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      prefix: -i

  annotated_fastq:
    type: File
    inputBinding:
      prefix: -f

  output_bam_filename:
    type: ['null', string]
    default: $( inputs.input_bam.basename.replace(".bam", "_fulcABWU.bam") )
    inputBinding:
      prefix: -o
      valueFrom: $( inputs.input_bam.basename.replace(".bam", "_fulcABWU.bam") )

outputs:
  output_bam:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_fulcABWU.bam") )
