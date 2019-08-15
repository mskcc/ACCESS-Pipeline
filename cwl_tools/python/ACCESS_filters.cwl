cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 20000
  coresMin: 1

baseCommand: [ACCESS_filters]

inputs:

  anno_maf:
    type: File
    inputBinding:
      prefix: --anno_maf

  fillout_maf:
    type: File
    inputBinding:
      prefix: --fillout_maf

  tumor_samplename:
    type: string
    inputBinding:
      prefix: --tumor_samplename

  normal_samplename:
    type: string
    inputBinding:
      prefix: --normal_samplename

  blacklist_file:
    type: File
    inputBinding:
      prefix: --blacklist_file

  tumor_detect_alt_thres:
    type: int
    inputBinding:
      prefix: --tumor_detect_alt_thres

  curated_detect_alt_thres:
    type: int
    inputBinding:
      prefix: --curated_detect_alt_thres

  DS_tumor_detect_alt_thres:
    type: int
    inputBinding:
      prefix: --DS_tumor_detect_alt_thres

  DS_curated_detect_alt_thres:
    type: int
    inputBinding:
      prefix: --DS_curated_detect_alt_thres

  normal_TD_min:
    type: int
    inputBinding:
      prefix: --normal_TD_min

  normal_vaf_germline_thres:
    type: float
    inputBinding:
      prefix: --normal_vaf_germline_thres

  tumor_TD_min:
    type: int
    inputBinding:
      prefix: --tumor_TD_min

  tumor_vaf_germline_thres:
    type: float
    inputBinding:
      prefix: --tumor_vaf_germline_thres

  tier_one_alt_min:
    type: int
    inputBinding:
      prefix: --tier_one_alt_min

  tier_two_alt_min:
    type: int
    inputBinding:
      prefix: --tier_two_alt_min

  min_n_curated_samples_alt_detected:
    type: int
    inputBinding:
      prefix: --min_n_curated_samples_alt_detected

  tn_ratio_thres:
    type: int
    inputBinding:
      prefix: --tn_ratio_thres

outputs:

  filtered_condensed_maf:
    type: File
    outputBinding:
      glob: '*_condensed.maf'

  filtered_maf:
    type: File
    outputBinding:
      glob: '*_filtered.maf'
