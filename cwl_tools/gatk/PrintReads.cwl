#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
#- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java
- $(inputs.java)

arguments:
- -Xmx4g
- -Djava.io.tmpdir=/ifs/work/scratch/
- -jar
# Todo: consolidate?
- $(inputs.gatk)
#- /opt/common/CentOS_6/gatk/GenomeAnalysisTK-3.3-0/GenomeAnalysisTK.jar
#- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar # v3.5
- -T
- PrintReads

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 10000
    coresMin: 8

doc: |
  None

inputs:
  java: string
  gatk: string

  out:
    type:
    - 'null'
    - string
    doc: Write output to this BAM filename instead of STDOUT
    inputBinding:
      prefix: --out

  input_file:
    type: File
    doc: Input file containing sequence data (SAM or BAM)
    inputBinding:
      prefix: --input_file

  reference_sequence:
    type: string
    inputBinding:
      prefix: --reference_sequence

  baq:
    type:
    - 'null'
    - string
    - type: array
      items: string
    doc: Type of BAQ calculation to apply in the engine (OFF| CALCULATE_AS_NECESSARY|
      RECALCULATE)
    inputBinding:
      prefix: --baq

  BQSR:
    type:
    - 'null'
    - string
    - File
    doc: Input covariates table file for on-the-fly base quality score recalibration
    inputBinding:
      prefix: --BQSR

  nct:
    type: int
    inputBinding:
      prefix: -nct

  EOQ:
    type: boolean
    inputBinding:
      prefix: -EOQ

outputs:
  out_bams:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out;
          return null;
        }

  out_bais:
    type: File?
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out.replace(/\.bam/,'') + ".bai";
          return null;
        }
