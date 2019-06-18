cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 4

arguments:
- $('/dmp/resources/prod/tools/bio/msisensor/production/msisensor')
- msi

stdout: $(inputs.sample_name + '_msi.stdout')
stderr: $(inputs.sample_name + '_msi.stderr')

inputs:

  microsatellites:
    type: File
    inputBinding:
      prefix: -d

  normal_bam:
    type: File
    inputBinding:
      prefix: -n
    secondaryFiles:
      - ^.bai

  tumor_bam:
    type: File
    inputBinding:
      prefix: -t
    secondaryFiles:
      - ^.bai

  sample_name:
    type: string
    inputBinding:
      prefix: -o
      valueFrom: $(self + '.msisensor')
    
  threads:
    type: int
    inputBinding:
      prefix: -b

outputs:

  output_dir:
    type: Directory
  
  msisensor_main:
    type: File
    outputBinding:
      glob: $(inputs.sample_name + '.msisensor')
  
  msisensor_somatic:
    type: File
    outputBinding:
      glob: $(inputs.sample_name + '.msisensor_somatic')

  msisensor_germline:
    type: File
    outputBinding:
      glob: $(inputs.sample_name + '.msisensor_germline')

  msisensor_distribution:
    type: File
    outputBinding:
      glob: $(inputs.sample_name + '.msisensor_dis')

  standard_out:
    type: stdout

  standard_err:
    type: stderr
