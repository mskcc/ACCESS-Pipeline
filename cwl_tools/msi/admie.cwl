cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 6

baseCommand: python

arguments:
- $(inputs.file_path + inputs.admie_script)

stdout: admie.stdout
stderr: admie.stderr

inputs:

  admie_script: string
  file_path: string

  project_name_msi:
    type: string?
    
  msisensor_allele_counts:
    type: Directory?
    inputBinding:
      prefix: --allele-counts

  allele_counts_list:
    type: File[]?
    inputBinding:
      prefix: --allele-list

  model:
    type: File
    inputBinding:
      prefix: --model
  
  coverage_data:
    type: Directory?
    inputBinding:
      prefix: --qc-directory
  
outputs:
  
  distance_vectors:
    type: File
    outputBinding:
      glob: $('distance_vectors.tsv')
  
  admie_results:
    type: File
    outputBinding:
      glob: $('msi_results.txt')
  
  # TODO: Fix the plots output on admie module
  plots:
    type: File[]?
    outputBinding:
      glob: '*_MSI_QC.pdf'

  standard_out:
    type: stdout

  standard_err:
    type: stderr
