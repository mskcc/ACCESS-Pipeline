#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java_8)
- -server
- -Xms8g
- -Xmx8g
- -cp
- $(inputs.marianas_path)
- org.mskcc.marianas.umi.duplex.postprocessing.SeparateBams

requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 1

inputs:
  java_8: string
  marianas_path: string

  sample: ../../resources/schema_defs/Sample.cwl#Sample

  collapsed_bam:
    type: File
    inputBinding:
      # Todo:
      position: 999

outputs:

  output_samples:
    name: output_samples
    type: ../../resources/schema_defs/Sample.cwl#Sample
    outputBinding:
      glob: '*.bam'
      # Todo: confirm that simp/dup bams are matched correctly
      outputEval: |
        ${
          var output_sample = inputs.samples;

          var simplex_duplex_bam = self.filter(function(x){return x.indexOf('simplex-duplex' > -1)}[0]);
          var duplex_bam = self.filter(function(x){return x.indexOf('BR-duplex' > -1)}[0]);

          output_sample.simplex_duplex_bam = simplex_duplex_bam;
          output_sample.duplex_bam = duplex_bam;

          return {'output_sample': output_sample}
        }
