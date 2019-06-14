cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 4

arguments:
- python
- $('/home/jayakumg/software/dev/ADMIE/admie-analyze.py')

inputs:

  project_name:
    type: string?
    
  msisensor_allele_counts:
    type: Directory
    inputBinding:
      prefix: --allele-counts

  model:
    type: File
    inputBinding:
      prefix: --model
  
  coverage_data:
    type: Directory?
    inputBinding:
      prefix: --qc_directory
  
  outfile:
    type: string?
    inputBinding:
      prefix: --output-file
      valueFrom: $('./' + self.project_name + '_' + self.outfile)


outputs:
  
  distance_vectors:
    type: File
    outputBinding:
      glob: $('distance_vectors.tsv')
  
  results:
    type: File
    outputBinding:
      glob: $('admie-output.txt')
  
  # TODO: Fix the plots output on admie module
  plots:
    type: File[]
    outputBinding:
      glob: $(inputs.msisensor_allele_counts + '/*_MSI_QC.pdf')