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
      prefix: --INPUT

  AS:
    type: ['null', string]
    doc: If true (default), then the sort order in the header file will be ignored.
      Default value - true. This option can be set to 'null' to clear the default
      value. Possible values - {true, false}
    inputBinding:
      prefix: --ASSUME_SORTED

  STOP_AFTER:
    type: ['null', string]
    doc: Stop after processing N reads, mainly for debugging. Default value - 0. This
      option can be set to 'null' to clear the default value.
    inputBinding:
      prefix: --STOP_AFTER

  output_name:
    type: string
    doc: Base name of output files. Required.
    inputBinding:
      prefix: --OUTPUT

  EXT:
    type: ['null', string]
    doc: Append the given file extension to all metric file names (ex. OUTPUT.insert_size_metrics.EXT).
      None if null Default value - null.
    inputBinding:
      prefix: --FILE_EXTENSION

  PROGRAM:
    type:
    - 'null'
    - type: array
      items: string
      inputBinding:
        prefix: --PROGRAM
    inputBinding:
      prefix:
    doc: List of metrics programs to apply during the pass through the SAM file. Possible
      values - {CollectAlignmentSummaryMetrics, CollectInsertSizeMetrics, QualityScoreDistribution,
      MeanQualityByCycle} This option may be specified 0 or more times. This option
      can be set to 'null' to clear the default list.

  INTERVALS:
    type: ['null', string]
    doc: An optional list of intervals to restrict analysis to. Only pertains to some
      of the PROGRAMs. Programs whose stand-alone CLP does not have an INTERVALS argument
      will silently ignore this argument. Default value - null.
    inputBinding:
      prefix: --INTERVALS

  DB_SNP:
    type: ['null', string]
    doc: VCF format dbSNP file, used to exclude regions around known polymorphisms
      from analysis by some PROGRAMs; PROGRAMs whose CLP doesn't allow for this argument
      will quietly ignore it. Default value - null.
    inputBinding:
      prefix: --DB_SNP

  UNPAIRED:
    type: ['null', string]
    doc: Include unpaired reads in CollectSequencingArtifactMetrics. If set to true
      then all paired reads will be included as well - MINIMUM_INSERT_SIZE and MAXIMUM_INSERT_SIZE
      will be ignored in CollectSequencingArtifactMetrics. Default value - false.
      This option can be set to 'null' to clear the default value. Possible values
      - {true, false}
    inputBinding:
      prefix: --INCLUDE_UNPAIRED

  QUIET:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --QUIET

  CREATE_MD5_FILE:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --CREATE_MD5_FILE

  CREATE_INDEX:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --CREATE_INDEX

  TMP_DIR:
    type: ['null', string]
    inputBinding:
      prefix: --TMP_DIR

  VERBOSITY:
    type: ['null', string]
    inputBinding:
      prefix: --VERBOSITY

  VALIDATION_STRINGENCY:
    type: ['null', string]
    inputBinding:
      prefix: --VALIDATION_STRINGENCY
    default: SILENT

  COMPRESSION_LEVEL:
    type: ['null', string]
    inputBinding:
      prefix: --COMPRESSION_LEVEL

  MAX_RECORDS_IN_RAM:
    type: ['null', string]
    inputBinding:
      prefix: --MAX_RECORDS_IN_RAM

  stderr:
    type: ['null', string]
    doc: log stderr to file
    inputBinding:
      prefix: --stderr

  stdout:
    type: ['null', string]
    doc: log stdout to file
    inputBinding:
      prefix: --stdout

  R:
    type:
    - 'null'
    - type: enum
      symbols: ['', GRCm38, ncbi36, mm9, GRCh37, GRCh38, hg18, hg19, mm10]
  H:
    type: ['null', string]
    inputBinding:
      prefix: --H

outputs:

  all_metrics:
    type: Directory
    outputBinding:
      glob: '.'

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
