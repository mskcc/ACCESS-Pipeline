cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    coresMin: 8

baseCommand: Rscript

arguments:
- $(inputs.loess_normalize_script)
- --slave
- --vanilla
- --args

inputs:

  loess_normalize_script: File

  project_name:
    type: string
    inputBinding:
      prefix: --runID
    doc: e.g. ACCESSv1-VAL-20180001

  coverage_file:
    type: File
    doc: coverage files, targets_nomapq.covg_interval_summary

  targets_coverage_annotation:
    type: File
    inputBinding:
      prefix: --targetAnnotations
    doc: ACCESS_targets_coverage.txt
      Full Path to text file of target annotations. Columns = (Chrom, Start, End, Target, GC_150bp, GeneExon, Cyt, Interval)

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
    type: File?
    outputBinding:
      glob: $('*tumor_loessnorm.pdf')

  normal_loess_pdf:
    type: File?
    outputBinding:
      glob: $('*normal_loessnorm.pdf')

