cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    coresMin: 8

baseCommand: R

arguments:
- --slave
- --vanilla
- --args

inputs:

  output_directory:
    type: string
    default: .
    inputBinding:
        position: 1

  project_name:
    type: string
    inputBinding:
      position: 2
    doc: e.g. ACCESSv1-VAL-20180001

  coverage_file:
    type: File
    inputBinding:
      position: 4
    doc: coverage files, targets_nomapq.covg_interval_summary

  targets_coverage_annotation:
    type: File
    inputBinding:
      position: 3
    doc: ACCESS_targets_coverage.txt
      Full Path to text file of target annotations. Columns = (Chrom, Start, End, Target, GC_150bp, GeneExon, Cyt, Interval)

  run_type:
    type: string
    inputBinding:
      position: 5
    doc: tumor or normal

  loess_normalize_script:
    type: File
    inputBinding:
      prefix: <
      position: 6
  

outputs:
  loess_tumors:
    type: File?
    outputBinding:
      glob: $('*tumor_ALL_intervalnomapqcoverage_loess.txt')

  loess_normals:
    type: File?
    outputBinding:
      glob: $('*normal_ALL_intervalnomapqcoverage_loess.txt')

  tumor_loess_pdf:
    type: File
    outputBinding:
      glob: $('*tumor_loessnorm.pdf')

  normal_loess_pdf:
    type: File?
    outputBinding:
      glob: $('*normal_loessnorm.pdf')

