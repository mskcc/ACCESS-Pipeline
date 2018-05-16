#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx60g
- -Djava.io.tmpdir=/scratch
- -jar
- $(inputs.abra)

requirements:
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl
  InitialWorkDirRequirement:
    listing: |
      $(inputs.input_bais.concat(inputs.input_bams))
  ResourceRequirement:
    ramMin: 62000
    coresMin: 8

# Todo: It would be nice to have this
# but unfortunately PATH is not a defined
# variable in the CWL parsing environment.
# For now we rely on including BWA at the beginning
# of our PATH before starting the run
#
#  EnvVarRequirement:
#    envDef:
#      PATH: $(inputs.bwa + ':' + PATH)

inputs:
  java: string
  abra: string
  samples: ../../resources/schema_defs/Sample.cwl#Sample[]

  input_bams:
    type:
      type: array
      items: File
    inputBinding:
      prefix: --in
      itemSeparator: ','

  input_bais:
    type:
      type: array
      items: File

  scratch_dir: string

  working_directory:
    type: string
    inputBinding:
      prefix: --working

  reference_fasta:
    type: string
    inputBinding:
      prefix: --ref

  targets:
    type: File
    inputBinding:
      prefix: --targets

  threads:
    type: int
    inputBinding:
      prefix: --threads

  kmer:
    type: string
    inputBinding:
      prefix: --kmer

  mad:
    type: int
    inputBinding:
      prefix: --mad

  out:
    type:
      type: array
      items: string
    inputBinding:
      itemSeparator: ','
      prefix: --out

outputs:

  output_samples:
    name: output_samples
    type: ../../resources/schema_defs/Sample.cwl#Sample[]
    outputBinding:
      glob: '*_IR.bam'
      # Todo: confirm that IR bams are matched correctly
      outputEval: |
        ${
          var output_samples = inputs.samples;

          for (var i = 0; i < output_samples.length; i++) {
            output_samples[i].ir_bam_1 = self[i];
          }

          return output_samples
        }
