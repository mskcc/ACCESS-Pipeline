cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    coresMin: 1
    ramMin: 10000

baseCommand: /usersoftware/core005/access/production/V1/ACCESS-Pipeline/cwl_tools/cnv/scripts/copynumber_tm.batchdiff_cfdna.R

inputs:

  project_name_cnv:
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

outputs:
  genes_file:
    type: File
    outputBinding:
      glob: $('*copynumber_segclusp.genes.txt')

  probes_file:
    type: File
    outputBinding:
      glob: $('*copynumber_segclusp.probes.txt')


  copy_pdf:
    type: File
    outputBinding:
      glob: $('*copynumber_segclusp.pdf')

  seg_files:
    type: File[]
    outputBinding:
      glob: $('*.seg')
