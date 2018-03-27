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
  doap:name: trimgalore
  doap:revision: 0.2.5
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
    inputBinding:
      prefix: -a

  adapter2:
    type: ['null', string]
    inputBinding:
      prefix: -a2

  length:
    type: ['null', string]
    inputBinding:
      prefix: -length
    default: '25'

  paired:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --paired

  gzip:
    type: ['null', boolean]
    default: false
    inputBinding:
      prefix: --gzip

  quality:
    type: ['null', string]
    inputBinding:
      prefix: -q
    default: '1'

  stringency:
    type: ['null', string]
    inputBinding:
      prefix: --stringency

  output_dir:
    type: ['null', string]
    inputBinding:
      prefix: --output_dir

  suppress_warn:
    type: ['null', boolean]
    default: true
    inputBinding:
      prefix: --suppress_warn

outputs:

  clfastq1:
    type: File
    outputBinding:
      glob: ${return inputs.fastq1.basename.replace(".fastq.gz", "_cl.fastq.gz")}

  clfastq2:
    type: File
    outputBinding:
      glob: ${return inputs.fastq2.basename.replace(".fastq.gz", "_cl.fastq.gz")}

  clstats1:
    type: File
    outputBinding:
      glob: ${return inputs.fastq1.basename.replace(".fastq.gz", "_cl.stats")}

  clstats2:
    type: File
    outputBinding:
      glob: ${return inputs.fastq2.basename.replace(".fastq.gz", "_cl.stats")}
