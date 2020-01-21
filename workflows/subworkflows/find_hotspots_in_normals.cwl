cwlVersion: v1.0

class: Workflow

doc: |
  Workflow to find hotspot VAFs from duplex (for Tumor sample) and unfiltered (for Normal sample) pileups.

  These inputs are all required to be sorted in the same order:

  sample_ids
  patient_ids
  sample_classes
  unfiltered_pileups
  duplex_pileups

requirements:
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_tools/schemas.yaml

inputs:
  run_tools: ../../resources/run_tools/schemas.yaml#run_tools
  sample_ids: string[]
  patient_ids: string[]
  sample_classes: string[]
  unfiltered_pileups: File[]
  duplex_pileups: File[]
  hotspot_list: File

outputs:

  hotspots_in_normals_data:
    type: File
    outputSource: find_hotspots_in_normals/hotspots_in_normals_data

  hotspots_in_normals_table_pdf:
    type: File
    outputSource: print_hotspots_in_normals_table/hotspots_in_normals_table_pdf

  hotspots_in_normals_plot:
    type: File
    outputSource: plot_hotspots_in_normals/hotspots_in_normals_plot

steps:

  find_hotspots_in_normals:
    run: ../../cwl_tools/bioinfo_utils/find_hotspots_in_normals.cwl
    in:
      run_tools: run_tools
      java:
        valueFrom: $(inputs.run_tools.java_8)
      bioinfo_utils:
        valueFrom: $(inputs.run_tools.bioinfo_utils)
      sample_ids: sample_ids
      patient_ids: patient_ids
      sample_classes: sample_classes
      unfiltered_pileups: unfiltered_pileups
      duplex_pileups: duplex_pileups
      hotspot_list: hotspot_list
    out: [hotspots_in_normals_data]

  print_hotspots_in_normals_table:
    run: ../../cwl_tools/bioinfo_utils/print_hotspots_in_normals_table.cwl
    in:
      table: find_hotspots_in_normals/hotspots_in_normals_data
    out: [hotspots_in_normals_table_pdf]

  plot_hotspots_in_normals:
    run: ../../cwl_tools/bioinfo_utils/plot_hotspots_in_normals.cwl
    in:
      hotspots_in_normals_data: find_hotspots_in_normals/hotspots_in_normals_data
    out: [hotspots_in_normals_plot]
