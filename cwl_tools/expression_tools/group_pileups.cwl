#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: ExpressionTool

doc: |
  Tool to group Tumor and Normal bams
  with the Normal pileup from the same patient

requirements:
  - class: InlineJavascriptRequirement

inputs:
  bams: File[]
  pileups: File[]
  sample_ids: string[]
  patient_ids: string[]
  sample_classes: string[]

outputs:
  matched_pileups:
    type:
      type: array
      items: File

expression: |
  ${
    // These lists are all in parallel sorted order
    var bams = inputs.bams;
    var pileups = inputs.pileups;
    var sample_ids = inputs.sample_ids;
    var patient_ids = inputs.patient_ids;
    var sample_classes = inputs.sample_classes;

    var matched_pileups = [];

    // For every bam
    for (var i = 0; i < bams.length; i++) {
      var current_bam = bams[i];
      var current_bam_sample_id = sample_ids[i];
      var current_bam_patient_id = patient_ids[i];
      var current_pileup_class = sample_classes[j];

      var found = false;

      // Look for the right pileup
      for (var j = 0; j < pileups.length; j++) {
        var current_pileup = pileups[j];
        var current_pileup_sample_id = sample_ids[j];
        var current_pileup_patient_id = patient_ids[j];

        // If they have matching patient IDs
        if (current_bam_patient_id === current_pileup_patient_id) {

          // And the current Pileup is a Normal
          if (current_pileup_class === 'Normal'){

            // Add this Pileup to the final matching list
            matched_pileups.push(current_pileup);
            found = true;

          }
        }
      }

      // If we never found a Normal pileup from the same patient for this Bam
      if (!found) {

        // Go through the pileups again
        for (var j = 0; j < pileups.length; j++) {
          var current_pileup = pileups[j];
          var current_pileup_sample_id = sample_ids[j];

          // And add the pileup that matches that Tumor sample
          if (current_bam_sample_id === current_pileup_sample_id) {
            matched_pileups.push(current_pileup);
          }

        }

      }
    }

    return {
      'matched_pileups': matched_pileups
    }
  }
