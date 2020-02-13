cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/collapsing_tools.yaml
  InitialWorkDirRequirement:
    listing:
      - entryname: pileups.tsv
        # This expression pairs each Tumor sample with its Duplex pileups,
        # and each Normal sample with its Unfiltered pileup
        entry: |-
          $(
            "sample_id	patient_id	sample_class	pileup\n" +
            inputs.sample_ids.map(function(sid, i) {
              if (inputs.sample_classes[i] == 'Tumor') {
                var pileup = inputs.duplex_pileups[i].path;
              } else {
                var pileup = inputs.unfiltered_pileups[i].path;
              }

              return sid + "\t" +
                inputs.patient_ids[i] + "\t" +
                inputs.sample_classes[i] + "\t" +
                pileup;
            }).join("\n")
          )

arguments:
- $(inputs.java)
- -server
- -Xms4g
- -Xmx4g
- -cp
- $(inputs.bioinfo_utils)
- org.mskcc.juber.commands.FindHotspotsInNormals
- pileups.tsv
- $(inputs.hotspot_list)

inputs:

  run_tools: ../../resources/schemas/collapsing_tools.yaml#run_tools

  java: string
  bioinfo_utils: File
  sample_ids: string[]
  patient_ids: string[]
  sample_classes: string[]
  unfiltered_pileups: File[]
  duplex_pileups: File[]
  hotspot_list: File

outputs:

  hotspots_in_normals_data:
    type: File
    outputBinding:
      glob: 'hotspots-in-normals.txt'
