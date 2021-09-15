cwlVersion: v1.0

class: CommandLineTool

requirements:
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/variants_tools.yaml
      - $import: ../../resources/schemas/params/vardict.yaml
  InlineJavascriptRequirement: {}
  ShellCommandRequirement: {}
  EnvVarRequirement:
    envDef:
      JAVA_HOME: "/opt/common/CentOS_6-dev/java/jdk1.8.0_31"
  ResourceRequirement:
    ramMin: 32000
    coresMin: 4
    outdirMax: 20000

arguments:
- $(inputs.vardict)
- -E
- $(inputs.column_for_region_end)
- -G
- $(inputs.reference_fasta)
# Todo: Should be T|N or just T? Why?
- -N
- $(inputs.tumor_sample_name)
- -c
- $(inputs.column_for_chromosome)
- -b
- $(inputs.tumor_bam.path + '|' + inputs.normal_bam.path)
- -g
- $(inputs.column_for_gene_name)
- -f
- $(inputs.allele_freq_thres)
- -S
- $(inputs.column_for_region_start)
- -r
- $(inputs.min_num_variant_reads)
- $(inputs.bed_file)
- shellQuote: false
  valueFrom: $('|')
- $(inputs.testsomatic)
- shellQuote: false
  valueFrom: $('|')
- $(inputs.var2vcf_paired)
- -A
- -N
- $(inputs.tumor_sample_name + '|' + inputs.normal_sample_name)
- -f
- $(inputs.allele_freq_thres)

stdout: $(inputs.output_file_name)

inputs:

  vardict: string
  testsomatic: string
  var2vcf_paired: string

  run_tools: ../../resources/schemas/variants_tools.yaml#run_tools
  vardict_params: ../../resources/schemas/params/vardict.yaml#vardict_params

  output_file_name: string
  bed_file: File

  reference_fasta:
    type: File
    doc: Reference fasta

  tumor_bam:
    type: File
    doc: Tumor bam
    secondaryFiles: [^.bai]

  normal_bam:
    type: File
    doc: Normal bam
    secondaryFiles: [^.bai]

  tumor_sample_name:
    type: string
    doc: Tumor Sample Name

  normal_sample_name:
    type: string
    doc: Normal Sample Name

  allele_freq_thres:
    type: float
    doc: The threshold for allele frequency

  min_num_variant_reads:
    type: int
    doc: The minimum number of reads to call a variant

  column_for_gene_name:
    type: int
    doc: The column for gene name, or segment annotation

  column_for_chromosome:
    type: int
    doc: The column for chromosome

  column_for_region_end:
    type: int
    doc: The column for region end, e.g. gene end

  column_for_region_start:
    type: int
    doc: The column for region start, e.g. gene start

  # Optional:

  C:
    type: boolean?
    doc: Indicate the chromosome names are just numbers, such as 1, 2, not chr1, chr2
    inputBinding:
      prefix: -C

  Q:
    type: string?
    doc: If set, reads with mapping quality less than INT will be filtered and ignored
    inputBinding:
      prefix: -Q

  q:
    type: string?
    doc: The phred score for a base to be considered a good call. Default - 25 (for
      Illumina) For PGM, set it to ~15, as PGM tends to under estimate base quality.
    inputBinding:
      prefix: -q

  th:
    type: string?
    doc: Threads count.
    inputBinding:
      prefix: -th

  x:
    type: string?
    doc: The number of nucleotide to extend for each segment, default - 0 -y
    inputBinding:
      prefix: -x

  X:
    type: string?
    doc: Extension of bp to look for mismatches after insersion or deletion. Default
      to 3 bp, or only calls when they're within 3 bp.
    inputBinding:
      prefix: -X

  z:
    type: string?
    doc: Indicate wehther is zero-based cooridates, as IGV does. Default - 1 for BED
      file or amplicon BED file. Use 0 to turn it off. When use -R option, it's set
      to 0AUTHOR. Written by Zhongwu Lai, AstraZeneca, Boston, USAREPORTING BUGS.
      Report bugs to zhongwu@yahoo.comCOPYRIGHT. This is free software - you are free
      to change and redistribute it. There is NO WARRANTY, to the extent permitted
      by law.
    inputBinding:
      prefix: -z

outputs:

  output:
    type: stdout
    secondaryFiles: [.tbi]
