#!/usr/bin/env cwl-runner

$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/
  doap: http://usefulinc.com/ns/doap#

$schemas:
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf
- http://usefulinc.com/ns/doap#

doap:release:
- class: doap:Version
  doap:name: cmo-trimgalore
  doap:revision: 0.2.5.mod
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 0.0.0

dct:creator:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsoni@mskcc.org

dct:contributor:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johnson
    foaf:mbox: mailto:johnsoni@mskcc.org

cwlVersion: v1.0

class: CommandLineTool

baseCommand:
# todo: consolidate trim_galore and all dependencies
- /opt/common/CentOS_6/perl/perl-5.20.2/bin/perl
- /opt/common/CentOS_6/trim_galore/Trim_Galore_v0.2.5/trim_galore

arguments:
# todo - use inputs
- --paired
- --gzip
- -q
- '1'
- --suppress_warn
- --stringency
- '3'
- --length
- '25'
- $(inputs.fastq1)
- $(inputs.fastq2)

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 16000
  coresMin: 2

doc: |
  None

inputs:

  fastq1:
    type: File

  fastq2:
    type: File

  adapter:
    type: ['null', string]
    doc: Adapter sequence to be trimmed. If not specified explicitely, the first 13
      bp of the Illumina adapter 'AGATCGGAAGAGC' will be used by default.
    inputBinding:
      prefix: -a

  adapter2:
    type: ['null', string]
    doc: Optional adapter sequence to be trimmed off read 2 of paired-end files. This
      option requires '--paired' to be specified as well.
    inputBinding:
      prefix: -a2

  length:
    type: ['null', string]
    doc: Discard reads that became shorter than length INT because of either quality
      or adapter trimming. A value of '0' effectively disables this behaviour. Default
      - 20 bp. For paired-end files, both reads of a read-pair need to be longer than
      <INT> bp to be printed out to validated paired-end files (see option --paired).
      If only one read became too short there is the possibility of keeping such unpaired
      single-end reads (see --retain_unpaired). Default pair-cutoff - 20 bp.
    inputBinding:
      prefix: -length
    default: '25'

  paired:
    type: ['null', boolean]
    default: true
    doc: This option performs length trimming of quality/adapter/RRBS trimmed reads
      for paired-end files. To pass the validation test, both sequences of a sequence
      pair are required to have a certain minimum length which is governed by the
      option --length (see above). If only one read passes this length threshold the
      other read can be rescued (see option --retain_unpaired). Using this option
      lets you discard too short read pairs without disturbing the sequence-by-sequence
      order of FastQ files which is required by many aligners. Trim Galore! expects
      paired-end files to be supplied in a pairwise fashion, e.g. file1_1.fq file1_2.fq
      SRR2_1.fq.gz SRR2_2.fq.gz ... .
    inputBinding:
      prefix: --paired

  gzip:
    type: ['null', boolean]
    default: false
    doc: Compress the output file with gzip. If the input files are gzip-compressed
      the output files will be automatically gzip compressed as well.
    inputBinding:
      prefix: --gzip

  quality:
    type: ['null', string]
    doc: Trim low-quality ends from reads in addition to adapter removal. For RRBS
      samples, quality trimming will be performed first, and adapter trimming is carried
      in a second round. Other files are quality and adapter trimmed in a single pass.
      The algorithm is the same as the one used by BWA (Subtract INT from all qualities;
      compute partial sums from all indices to the end of the sequence; cut sequence
      at the index at which the sum is minimal). Default Phred score - 20.
    inputBinding:
      prefix: -q
    default: '1'

  stringency:
    type: ['null', string]
    doc: Overlap with adapter sequence required to trim a sequence. Defaults to a
      very stringent setting of '1', i.e. even a single bp of overlapping sequence
      will be trimmed of the 3' end of any read.-e <ERROR RATE> Maximum allowed error
      rate (no. of errors divided by the length of the matching region) (default -
      0.1)
    inputBinding:
      prefix: --stringency

  output_dir:
    type: ['null', string]
    doc: If specified all output will be written to this directory instead of the
      current directory.
    inputBinding:
      prefix: --output_dir

  suppress_warn:
    type: ['null', boolean]
    default: true
    doc: If specified any output to STDOUT or STDERR will be suppressed.RRBS-specific
      options (MspI digested material) -
    inputBinding:
      prefix: --suppress_warn

outputs:

  clfastq1:
    type: File
    outputBinding:
      glob: ${ return inputs.fastq1.basename.replace(".fastq.gz", "_cl.fastq.gz") }

  clfastq2:
    type: File
    outputBinding:
      glob: ${ return inputs.fastq2.basename.replace(".fastq.gz", "_cl.fastq.gz") }

  clstats1:
    type: File
    outputBinding:
      glob: ${ return inputs.fastq1.basename.replace(".fastq.gz", "_cl.stats") }

  clstats2:
    type: File
    outputBinding:
      glob: ${ return inputs.fastq2.basename.replace(".fastq.gz", "_cl.stats") }
