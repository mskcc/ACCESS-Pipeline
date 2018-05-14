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
    secondaryFiles:
    - ^.bai

  scratch_dir:
    type: string
  patient_id:
    type: string

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
    type: string[]
    default: $(inputs.input_bams.map(function(b){return b.basename.replace(".bam", "_IR.bam")}))
    inputBinding:
      itemSeparator: ','
      prefix: --out
      valueFrom: $(inputs.input_bams.map(function(b){return b.basename.replace(".bam", "_IR.bam")}))

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
            output_samples.bams[i].ir_bam = self[i];
          }

          return output_samples
        }
