cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    coresMin: 8

baseCommand: Rscript

arguments:
- $(inputs.copy_number_script)
- --slave
- --vanilla
- --args

inputs:

  copy_number_script: File

  project_name:
    type: string
    inputBinding:
      prefix: --runID
    doc: e.g. ACCESSv1-VAL-20180001

  targets_coverage_annotation:
    type: File
    inputBinding:
      prefix: --targetAnnotations
    doc: ACCESS_targets_coverage.txt
      Full Path to text file of target annotations. Columns = (Chrom, Start, End, Target, GC_150bp, GeneExon, Cyt, Interval)

  loess_normals:
    type: File
    doc: normal_ALL_intervalnomapqcoverage_loess.txt

  loess_tumors:
    type: File
    doc: tumor_ALL_intervalnomapqcoverage_loess.txt

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

  #include seg files?
