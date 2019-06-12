cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    coresMin: 1
    ramMin: 10000

baseCommand: R

arguments:
- --slave
- --vanilla
- --file=$(inputs.loess_normalize_script.path)
- --args
- $(runtime.outdir)

stdout: $(inputs.run_type.path + '_loess.stdout')
stderr: $(inputs.run_type.path + '_loess.stderr')

inputs:

  project_name:
    type: string
    inputBinding:
      position: 1
    doc: e.g. ACCESSv1-VAL-20180001

  coverage_file:
    type: File
    inputBinding:
      position: 3
    doc: coverage files, targets_nomapq.covg_interval_summary

  targets_coverage_annotation:
    type: File
    inputBinding:
      position: 2
    doc: ACCESS_targets_coverage.txt
      Full Path to text file of target annotations. Columns = (Chrom, Start, End, Target, GC_150bp, GeneExon, Cyt, Interval)

  run_type:
    type: string
    inputBinding:
      position: 4
    doc: tumor or normal

  loess_normalize_script: File


outputs:
  loess_text:
    type: File
    outputBinding:
      glob: $('*_ALL_intervalnomapqcoverage_loess.txt')

  loess_pdf:
    type: File
    outputBinding:
      glob: $('*_loessnorm.pdf')

  standard_out:
    type: stdout

  standard_err:
    type: stderr

