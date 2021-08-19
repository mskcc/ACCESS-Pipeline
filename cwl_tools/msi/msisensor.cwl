cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 20000 # todo: how to get 4GB when dividing by 4!!!!!!!!!!....
    coresMin: 4

arguments:
# todo: ensure 0.2 is first in $PATH
# or supply msisensor as run_tool
- $(inputs.msisensor)
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
