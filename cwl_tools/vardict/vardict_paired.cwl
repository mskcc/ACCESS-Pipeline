cwlVersion: v1.0

class: CommandLineTool

requirements:
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_params/schemas/vardict.yaml
  InlineJavascriptRequirement: {}
  ShellCommandRequirement: {}
  ResourceRequirement:
    ramMin: 32000
    coresMin: 4

arguments:
- /opt/common/CentOS_6-dev/vardict/v1.5.1/bin/VarDict
- -E
- $(inputs.E)
- -G
- $(inputs.G)
# Todo: Should be T|N or just T? Why?
- -N
- $(inputs.N)
- -c
- $(inputs.c)
- -b
- $(inputs.b.path + '|' + inputs.b2.path)
- -g
- $(inputs.g)
- -f
- $(inputs.f)
- -S
- $(inputs.S)
- -r
- $(inputs.r)
- $(inputs.bed_file)
- shellQuote: false
  valueFrom: $('|')
- /opt/common/CentOS_6-dev/vardict/v1.5.1/vardict_328e00a/testsomatic.R
- shellQuote: false
  valueFrom: $('|')
- /opt/common/CentOS_6-dev/vardict/v1.5.1/vardict_328e00a/var2vcf_paired.pl
- -N
- $(inputs.N + '|' + inputs.N2)
- -f
- $(inputs.f)

stdout: $(inputs.output_file_name)

inputs:

  vardict_params: ../../resources/run_params/schemas/vardict.yaml#vardict_params
  output_file_name: string

  b:
    type: File
    doc: Tumor bam
    secondaryFiles: [^.bai]

  b2:
    type: File
    doc: Normal bam
    secondaryFiles: [^.bai]

  bed_file:
    type: File

  c:
    type: int
    doc: The column for chromosome

  S:
    type: int
    doc: The column for region start, e.g. gene start

  E:
    type: int
    doc: The column for region end, e.g. gene end

  f:
    type: string
    doc: The threshold for allele frequency

  N:
    type: string
    doc: Tumor Sample Name

  N2:
    type: string
    doc: Normal Sample Name

  g:
    type: int
    doc: The column for gene name, or segment annotation

  G:
    type: File
    doc: Reference fasta

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
