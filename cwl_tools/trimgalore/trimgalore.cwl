#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.perl)
- $(inputs.trimgalore)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 16000
    coresMin: 2
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl

doc: |
  None

inputs:
  perl: string
  trimgalore: string
  sample: ../../resources/schema_defs/Sample.cwl#Sample

  fastqc_path:
    type: ['null', string]
    inputBinding:
      prefix: --path_to_fastqc

  cutadapt_path:
    type: ['null', string]
    inputBinding:
      prefix: --path_to_cutadapt

  fastq1:
    type: File
    inputBinding:
      # Todo: not ok
      position: 999

  fastq2:
    type: File
    inputBinding:
      # Todo: not ok
      position: 1000

  adapter:
    type: ['null', string]
    inputBinding:
      prefix: -a

  adapter2:
    type: ['null', string]
    inputBinding:
      prefix: -a2

  # Todo: use inputs instead of defaults
  length:
    type: ['null', string]
    default: '25'
    inputBinding:
      prefix: -length

  paired:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --paired

  gzip:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --gzip

  quality:
    type: ['null', string]
    default: '1'
    inputBinding:
      prefix: -q

  stringency:
    type: ['null', string]
    default: '3'
    inputBinding:
      prefix: --stringency

  suppress_warn:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --suppress_warn

outputs:

  output_sample:
    name: output_sample
    type: ../../resources/schema_defs/Sample.cwl#Sample
    outputBinding:
      glob: '*'
      outputEval: |
        ${
          var output_sample = inputs.sample;

          output_sample.clfastq1 = self.filter(function(x) {
            return x.basename === inputs.fastq1.basename.replace('.fastq.gz', '_cl.fastq.gz')
          })[0];

          output_sample.clfastq2 = self.filter(function(x){
            return x.basename === inputs.fastq2.basename.replace('.fastq.gz', '_cl.fastq.gz')
          })[0];

          output_sample.clstats1 = self.filter(function(x) {
            return x.basename === inputs.fastq1.basename.replace('.fastq.gz', '_cl.stats')
          })[0];

          output_sample.clstats2 = self.filter(function(x){
            return x.basename === inputs.fastq2.basename.replace('.fastq.gz', '_cl.stats')
          })[0];

          return output_sample
        }
