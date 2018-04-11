#!/usr/bin/env cwl-runner

cwlVersion: cwl:v1.0

class: CommandLineTool

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
- -Xmx20g
- -Djava.io.tmpdir=/scratch
- -jar
# Todo: consolidate?
- /opt/common/CentOS_6/gatk/GenomeAnalysisTK-3.3-0/GenomeAnalysisTK.jar
- -T
- FindCoveredIntervals

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 22000
    coresMin: 1

doc: |
  None

inputs:

# todo: cleaner way to provide inputs after arguments
# https://www.biostars.org/p/303637/
  bams:
    type:
      type: array
      items: File
      inputBinding:
        prefix: --input_file
        position: 100

  reference_sequence:
    type: string
    inputBinding:
      prefix: --reference_sequence

# todo: How to programatically use "intervals" parameter only during testing?
  intervals:
    type:
    - 'null'
    - type: array
      items: string
      inputBinding:
        prefix: --intervals
        position: 100

  min_base_quality:
    type: int
    inputBinding:
      prefix: --minBaseQuality
      position: 100

  min_mapping_quality:
    type: int
    inputBinding:
      prefix: --minMappingQuality
      position: 100

  coverage_threshold:
    type: int
    inputBinding:
      prefix: --coverage_threshold
      position: 100

  read_filters:
    type:
      type: array
      items: string
      inputBinding:
        prefix: --read_filter
        position: 100
        # todo: there should be a better way to specify multiple arguments with same prefix
        # https://www.biostars.org/p/303633/

  out:
    type: string
    inputBinding:
      prefix: --out
      position: 100

outputs:

  fci_list:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out;
          return null;
        }
