#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0
baseCommand: ["sh", "build_samplesheet.sh"]

requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entryname: build_samplesheet.sh
        entry: |-
          echo "Lane,Sample_ID,Sample_Plate,Sample_Well,I7_Index_ID,index,index2,Sample_Project,Description"
          echo "${
            return inputs.samples.map(function(x) { 
              return Object.values(x).join(",")
            }).join("\n");
          }"
inputs:
  samples:
    type:
      type: array
      items:
        type: record
        fields:
          lane:
            type: string
          sample_id:
            type: string
          sample_plate:
            type: string
          sample_well:
            type: string
          17_index_id:
            type: string
          index:
            type: string
          index2:
            type: string
          sample_project:
            type: string
          description:
            type: string?

outputs:
  out:
    type: stdout
stdout: sample_sheet.csv
