cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java_8)
- -server
- -Xms8g
- -Xmx8g
- -cp
- $(inputs.marianas_path)
- org.mskcc.marianas.umi.duplex.fastqprocessing.ProcessLoopUMIFastq

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.fastq1)
      - $(inputs.fastq2)
      - $(inputs.sample_sheet)
  - class: ResourceRequirement
    ramMin: 30000
    coresMin: 1
    outdirMax: 30000

inputs:
  java_8: string
  marianas_path: string

  fastq1:
    type: File
    inputBinding:
      position: 1

  fastq2: File
  sample_sheet: File

  umi_length:
    type: int
    inputBinding:
      position: 2

  output_project_folder:
    type: string
    inputBinding:
      position: 3

  # Since IGO uses the INVESTIGATOR_SAMPLE_IDs,
  # we need to change these to the CMO_SAMPLE_IDs
  investigator_sample_id: string
  add_rg_SM: string

outputs:

  # Todo - We rely on the **/ because Marianas outputs to a folder
  # which is named by the parent folder of the fastq,
  # which is randomly generated by Toil
  processed_fastq_1:
    type: File
    outputBinding:
      glob: ${ return '**/' + inputs.fastq1.basename }
      outputEval: |
        ${
          self[0].basename = inputs.fastq1.basename.replace(inputs.investigator_sample_id, inputs.add_rg_SM);
          return self[0]
        }

  processed_fastq_2:
    type: File
    outputBinding:
      glob: ${ return '**/' + inputs.fastq1.basename.replace('_R1_', '_R2_') }
      outputEval: |
        ${
          self[0].basename = inputs.fastq1.basename.replace('_R1_', '_R2_').replace(inputs.investigator_sample_id, inputs.add_rg_SM);
          return self[0]
        }

  clipping_info:
    type: File
    outputBinding:
      glob: ${ return '**/info.txt' }
      outputEval: |
        ${
          self[0].basename = inputs.fastq1.basename.replace(inputs.investigator_sample_id, inputs.add_rg_SM).split('_R1_')[0] + '_info.txt';
          return self[0]
        }

  clipping_dir:
    type: Directory
    outputBinding:
      glob: '*/'
      outputEval: |
        ${
          self[0].basename = inputs.fastq1.basename.replace(inputs.investigator_sample_id, inputs.add_rg_SM).split('_R1_')[0] + '_umi_clipping_results';
          return self[0]
        }
