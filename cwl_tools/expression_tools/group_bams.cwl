#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  - class: InlineJavascriptRequirement

inputs:

  bams: File[]
  patient_ids: string[]


outputs:

  grouped_bams:
    type:
      type: array
      items:
        type: array
        items: File
#      secondaryFiles: ['^.bai']

  grouped_patient_ids:
    type:
      type: array
      items: string

  sample_ids:
    type:
      type: array
      items: string

  sample_classes:
    type:
      type: array
      items: string

expression: |
  ${
    var found;

    // This will become a list of lists,
    // with each sublist holding all Bams for that patient
    var grouped_bams = [];

    // This is a list with patient IDs that correspond to these bams^
    var matching_patient_ids = [];

    // This will hold the re-ordered sample ids
    var ordered_sample_ids = [];

    // This will hold the re-ordered


    // For each Bam in our input Bams
    for (var i = 0; i < inputs.bams.length; i++) {

      found = false;
      var current_patient_id = inputs.patient_ids[i];

      // Check the patient IDs for the Bam groups we've created
      for (var j = 0; j < grouped_bams.length; j++) {

        // If the current Bam's patient ID matches this group's patient ID
        if (matching_patient_ids[j] === current_patient_id) {

          // Add it to this group
          grouped_bams[j].push(inputs.bams[i]);
          found = true;

        }
      }

      // If we didn't find this patient ID in any of our groups,
      if (!found) {

        // add a new group with this bam,
        grouped_bams.push([inputs.bams[i]]);

        // and add a new corresponding patient ID
        matching_patient_ids.push(current_patient_id);

      }
    }

    return {
      "grouped_bams": grouped_bams,
      "grouped_patient_ids": matching_patient_ids
    };
  }
