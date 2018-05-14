#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schema_defs/Sample.cwl

inputs:

  samples:
    type:
      type: array
      items: ../../resources/schema_defs/Sample.cwl#Sample

outputs:

  grouped_samples:
    type:
      type: array
      items:
        type: array
        items: ../../resources/schema_defs/Sample.cwl#Sample

expression: |
  ${
    // This will become a list of lists,
    // with each sublist holding all Bams for that patient
    var grouped_samples = [];

    // For each Sample in our input Bams
    for (var i = 0; i < inputs.samples.length; i++) {
      found = false;
      var current_patient_id = inputs.samples[i].patient_id;

      // Check the patient IDs for the Bam groups we've created
      for (var j = 0; j < grouped_samples.length; j++) {

        // If the current sample's patient ID matches this group's patient ID
        if (inputs.samples[j].patient_id === current_patient_id) {
          // Add it to this group
          grouped_samples[j].push(inputs.samples[i]);
          found = true;
        }
      }

      // If we didn't find this patient ID in any of our groups,
      if (!found) {
        // add a new group with this bam,
        grouped_samples.push([inputs.samples[i]]);
      }
    }

    return {
      'grouped_samples': grouped_samples
    };
  }
