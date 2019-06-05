cwlVersion: v1.0

class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    coresMin: 8


inputs:

  project_name:
    type: string
    inputBinding:
      prefix: --runID
    doc: e.g. ACCESSv1-VAL-20180001

  qsub:
    type: 
    - 'null'
    - type: string
    inputBinding:
      prefix: --qsubPath
    doc: Full Path to the qsub executables of SGE

  bsub:
    type:
    - 'null'
    - type: string
    inputBinding:
      prefix: --bsubPath
    doc: Full Path to the bsub executables of LSF

  loess_normalize_script:
    type:
    - 'null'
    - type: File
    inputBinding:
      prefix: --loess
    doc: Full Path to the loess normalization R script

  copy_number_script:
    type:
    - 'null'
    - type: File
    inputBinding:
      prefix: --copynumber
    doc: Full Path to the copy number R script

  queue:
    type:
    - 'null'
    - type: string
    inputBinding:
      prefix: --queue
    doc: test.q or clin2.q, Name of the SGE queue

  r_path:
    type:
    - 'null'
    - type: string
    inputBinding:
      prefix: --RPATH
    doc: Path to R executable

  tumor_manifest:
    type: File
    inputBinding:
      prefix: --tumorManifest
    doc: tumor_manifest.txt
      Full path to the tumor sample manifest, tab serparated BAM path, patient sex

  normal_manifest:
    type: File
    inputBinding:
      prefix: --normalManifest
    doc: normal_manifest.txt
      Full path to the normal sample manifest, tab serparated BAM path, patient sex

  targets_coverage_bed:
    type: File?
    inputBinding:
      prefix: --bedTargets
    doc: ACCESS_targets_coverage.bed
      Full Path to BED file of panel targets

  targets_coverage_annotation:
    type: File?
    inputBinding:
      prefix: --targetAnnotations
    doc: ACCESS_targets_coverage.txt
      Full Path to text file of target annotations. Columns = (Chrom, Start, End, Target, GC_150bp, GeneExon, Cyt, Interval)

  reference_fasta:
    type: File?
    inputBinding:
      prefix: --genomeReference
    doc: Homo_Sapeins_hg19.fasta
      Full Path to the reference fasta file

  output:
    type: Directory
    inputBinding:
      prefix: --outDir
    doc: Full Path to the output dir

outputs:

  output_files:
    type: File[]
    outputBinding:
      glob: '*.txt'

