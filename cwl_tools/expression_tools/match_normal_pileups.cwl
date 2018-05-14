#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: ExpressionTool

doc: |
  Tool to group Tumor and Normal bams
  with the Normal pileup from the same patient

requirements:
  - class: InlineJavascriptRequirement

inputs:
  samples: ../../resources/schema_defs/Sample.cwl#Sample[]

outputs:
  samples_with_matched_normal_pileups:
    type: ../../resources/schema_defs/Sample.cwl#Sample[]

expression: |
  ${
    var samples = inputs.samples;

    for (var i = 0; i < samples.length; i++) {
      if (samples[i].class === 'Tumor') {

        for (var j = 0; j < samples.length; j++) {

          if (samples[i].patient_id === samples[j].patient_id) {
            if (samples[j].class === 'Normal') {
              samples[i].normal_pileup = samples[j].pileup;
            }
          }

        }
      } else {
        samples[i].normal_pileup = samples[i].pileup;
      }
    }

    return {
      'samples_with_matched_normal_pileups': samples
    }
  }
