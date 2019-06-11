cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    coresMin: 8

baseCommand: python

arguments:
- $(inputs.coverage_script)

inputs:

  coverage_script: File

  project_name:
    type: string
    inputBinding:
      prefix: --runID
    doc: e.g. ACCESSv1-VAL-20180001

  threads:
    type: int
    inputBinding:
      prefix: --threads
    doc: Number of Threads to be used to generate coverage metrics

  tumor_sample_list:
    type: File
    inputBinding:
      prefix: --tumorManifest
    doc: tumor_manifest.txt
      Full path to the tumor sample manifest, tab serparated BAM path, patient sex

  normal_sample_list:
    type: File
    inputBinding:
      prefix: --normalManifest
    doc: normal_manifest.txt
      Full path to the normal sample manifest, tab serparated BAM path, patient sex

  targets_coverage_bed:
    type: File
    inputBinding:
      prefix: --bedTargets
    doc: ACCESS_targets_coverage.bed
      Full Path to BED file of panel targets

  reference_fasta:
    type: File
    inputBinding:
      prefix: --genomeReference
    doc: Homo_Sapeins_hg19.fasta
      Full Path to the reference fasta file

outputs:
  tumors_covg:
    type: File
    outputBinding:
      glob: $('*tumors_targets_nomapq.covg_interval_summary')

  normals_covg:
    type: File
    outputBinding:
      glob: $('*normals_targets_nomapq.covg_interval_summary')

  bam_list:
    type: File
    outputBinding:
      glob: $('*_bams.list')
