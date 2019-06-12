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
- --file=$(inputs.copy_number_script.path)
- --args
stdout: copy_number.stdout
stderr: copy_number.stderr

inputs:

  project_name:
    type: string
    inputBinding:
      position: 1
    doc: e.g. ACCESSv1-VAL-20180001

  targets_coverage_annotation:
    type: File
    inputBinding:
      position: 3
    doc: ACCESS_targets_coverage.txt
      Full Path to text file of target annotations. Columns = (Chrom, Start, End, Target, GC_150bp, GeneExon, Cyt, Interval)

  loess_normals:
    type: File
    inputBinding:
      position: 2
    doc: normal_ALL_intervalnomapqcoverage_loess.txt

  loess_tumors:
    type: File
    inputBinding:
      position: 4
    doc: tumor_ALL_intervalnomapqcoverage_loess.txt

  do_full:
    type: string
    inputBinding:
      position: 5
    doc: either 'FULL' or 'MIN'

  copy_number_script: File

outputs:
  genes_file:
    type: File
    outputBinding:
      glob: $('*copynumber_segclusp.genes.txt')

  probes_file:
    type: File
    outputBinding:
      glob: $('*copynumber_segclusp.probes.txt')

  intragenic_file:
    type: File
    outputBinding:
      glob: $('*copynumber_segclusp.intragenic.txt')

  copy_pdf:
    type: File
    outputBinding:
      glob: $('*copynumber_segclusp.pdf')

  seg_files:
    type: File[]
    outputBinding:
      glob: $('*.seg')

  standard_out:
    type: stdout

  standard_err:
    type: stderr
