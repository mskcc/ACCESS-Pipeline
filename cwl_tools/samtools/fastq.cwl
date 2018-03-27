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
  doap:name: samtools
  doap:revision: 1.3.1
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
    foaf:mbox: mailto:johnsonsi@mskcc.org

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

baseCommand:
- /opt/common/CentOS_6-dev/bin/current/samtools

arguments:
- shellQuote: false
# todo: need this on separate lines
# todo: need this to not be fulcrum-specific (just remove "_postFulcrum" in the filename)
  valueFrom: fastq -1 $( inputs.input_bam.basename.replace(".bam", "_R1.fastq") ) -2 $( inputs.input_bam.basename.replace(".bam", "_R2.fastq") ) $(inputs.input_bam.path)

inputs:

  input_bam:
    type: File

outputs:

  output_read_1:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_R1.fastq") )

  output_read_2:
    type: File
    outputBinding:
      glob: $( inputs.input_bam.basename.replace(".bam", "_R2.fastq") )
