#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: ExpressionTool

doc: |
  Tool to group Tumor and Normal bams
  with the Normal pileup from the same patient

requirements:
  - class: InlineJavascriptRequirement

inputs:

  pileups: File[]
  bams: File[]
  patient_ids: string[]
  class_list: string[]

outputs:

  ordered_pileups:
    type:
      type: array
      items: File
#      secondaryFiles: ['^.bai']

  ordered_bams:
    type:
      type: array
      items: File

  ordered_patient_ids:
    type:
      type: array
      items: string


# Todo: Currently, this tool does not handle the following situations:
#
# 1. Tumor sample with no Normal (these samples will not proceed)
# 2. Any sample with multiple normals (the first pileup will be chosen for both)
#
expression: |
  ${
    var pileups = inputs.pileups;
    var bams = inputs.bams;
    var patient_ids = inputs.patient_ids;
    var class_list = inputs.class_list;

    var ordered_bams = [];
    var ordered_pileups = [];
    var ordered_patient_ids = [];

    // For each pileup
    for (var i = 0; i < pileups.length; i++) {
      var current_pileup = pileups[i];
      var current_patient_id = patient_ids[i].replace('-', '_');
      var current_class = class_list[i];

      // If it is a normal pileup
      if (current_class.indexOf('Normal') > -1) {

        // Go through the input bams
        for (var j = 0; j < inputs.bams.length; j++) {
          var current_bam = inputs.bams[j];

          // If the current bam matches the current patient ID for this normal pileup
          if (current_bam.basename.replace('-', '_').indexOf(current_patient_id) > -1) {

            // Store the current bam
            ordered_bams.push(current_bam);
            // Store the matching normal pileup
            ordered_pileups.push(current_pileup);
            // And store the matching patient ID
            ordered_patient_ids.push(current_patient_id);

          }
        }
      }
    }

    return {
      'ordered_bams': ordered_bams,
      'ordered_pileups': ordered_pileups,
      'ordered_patient_ids': ordered_patient_ids
    }
  }
