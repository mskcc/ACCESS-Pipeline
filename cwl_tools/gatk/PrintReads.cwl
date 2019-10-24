cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx4g
- -jar
# Todo: consolidate?
- $(inputs.gatk)
- -T
- PrintReads

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 10000
    coresMin: 8
    outdirMax: 50000

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
