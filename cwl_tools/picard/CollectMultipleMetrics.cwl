cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    ramMin: 20000
    coresMin: 1
    outdirMax: 20000

arguments:
- $(inputs.java)
- -Xmx4g
- -jar
- $(inputs.picard)
- CollectMultipleMetrics

inputs:

  java: string
  picard: string

  input_bam:
    type:
    - File
    - type: array
      items: string
    inputBinding:
      prefix: INPUT=

  AS:
    type: ['null', boolean]
    doc: If true (default), then the sort order in the header file will be ignored.
      Default value - true. This option can be set to 'null' to clear the default
      value. Possible values - {true, false}
    default: false
    inputBinding:
      prefix: ASSUME_SORTED=

  output_name:
    type: string
    doc: Base name of output files. Required.
    inputBinding:
      prefix: OUTPUT=

  PROGRAM:
    type:
    - 'null'
    - type: array
      items: string
      inputBinding:
        prefix: PROGRAM=
    doc: List of metrics programs to apply during the pass through the SAM file. Possible
      values - {CollectAlignmentSummaryMetrics, CollectInsertSizeMetrics, QualityScoreDistribution,
      MeanQualityByCycle} This option may be specified 0 or more times. This option
      can be set to 'null' to clear the default list.

  TMP_DIR:
    type: ['null', string]
    inputBinding:
      prefix: TMP_DIR

  VALIDATION_STRINGENCY:
    type: ['null', string]
    inputBinding:
      prefix: VALIDATION_STRINGENCY=
    default: LENIENT

outputs:

  all_metrics:
    type: Directory
    outputBinding:
      glob: .
      outputEval: |
        ${
          self[0].basename = inputs.output_name + '_picard_metrics';
          return self[0]
        }

  qual_file:
    type: File?
    outputBinding:
      glob: |
        ${
          if (inputs.O)
            return inputs.O.concat('.quality_by_cycle_metrics');
          return null;
        }

  qual_hist:
    type: File?
    outputBinding:
      glob: |
        ${
          if (inputs.O)
            return inputs.O.concat('.quality_by_cycle.pdf');
          return null;
        }

  is_file:
    type: File?
    outputBinding:
      glob: |
        ${
          if (inputs.O)
            return inputs.O.concat('.insert_size_metrics');
          return null;
        }

  is_hist:
    type: File?
    outputBinding:
      glob: |
        ${
          if (inputs.O)
            return inputs.O.concat('.insert_size_histogram.pdf');
          return null;
        }
