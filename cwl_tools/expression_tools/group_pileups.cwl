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

# Todo:
#
# Much easier to just rely on parallel sorted order,
# rather than exhaustive search through both lists.
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
      var current_bam_class = sample_classes[i];

      var found = false;

      // Look for the right pileup
      for (var j = 0; j < pileups.length; j++) {
        var current_pileup = pileups[j];
        var current_pileup_sample_id = sample_ids[j];
        var current_pileup_patient_id = patient_ids[j];
        var current_pileup_class = sample_classes[j];

        // If they have matching patient IDs
        if (current_bam_patient_id === current_pileup_patient_id) {

          // And we are matching a Tumor with a corresponding Normal Pileup
          if (current_bam_class === 'Tumor' && current_pileup_class === 'Normal') {

            // Add this Pileup to the final matching list
            matched_pileups.push(current_pileup);
            found = true;
            break;

          // Otherwise, if the Sample is Normal, and we found the matching Pileup for this sample
          var bam_is_normal = current_bam_class === 'Normal';
          var pileup_is_normal = current_pileup_class === 'Normal';
          var sample_ids_match = current_bam_sample_id === current_pileup_sample_id;

          } else if (bam_is_normal && pileup_is_normal && sample_ids_match) {

            // Add this Pileup to the final matching list
            matched_pileups.push(current_pileup);
            found = true;
            break;
          }
        }
      }

      // If we never found a Normal pileup from the same patient for this Bam
      if (!found) {

        // Go through the pileups again
        for (var j = 0; j < pileups.length; j++) {
          var current_pileup = pileups[j];
          var current_pileup_sample_id = sample_ids[j];

          // And add the Tumor pileup that matches that Tumor sample
          if (current_bam_sample_id === current_pileup_sample_id) {
            matched_pileups.push(current_pileup);
            break;
          }
        }
      }
    }

    return {
      'matched_pileups': matched_pileups
    }
  }
