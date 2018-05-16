#!/usr/bin/env cwl-runner

cwlVersion: cwl:v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx20g
- -Djava.io.tmpdir=$(inputs.tmp_dir)
- -jar
- $(inputs.gatk)
- -T
- FindCoveredIntervals

requirements:
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl
  InitialWorkDirRequirement:
    listing: |
      $(inputs.bais.concat(inputs.bams))
  ResourceRequirement:
    ramMin: 22000
    coresMin: 1

doc: |
  None

inputs:
  tmp_dir: string
  java: string
  gatk: string
  samples: ../../resources/schema_defs/Sample.cwl#Sample[]

# Todo: cleaner way to provide inputs after arguments
# https://www.biostars.org/p/303637/
  bams:
    type:
      type: array
      items: File
      inputBinding:
        prefix: --input_file
        position: 100

  bais:
    type:
      type: array
      items: File

  reference_sequence:
    type: string
    inputBinding:
      prefix: --reference_sequence

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

  ignore_misencoded_base_qualities:
    type: boolean?
    default: false
    inputBinding:
      prefix: --allow_potentially_misencoded_quality_scores
      position: 100

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
