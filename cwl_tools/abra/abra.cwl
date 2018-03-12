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
  doap:name: abra
  doap:revision: 2.14
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

#cmd =
# args.JAVA + " -Xmx60g -jar " + args.ABRA +
#" --in " + inBamList +
#" --out " + outBamList +
#" --ref " + args.ref +
#" --targets " + args.targetRegion +
#" --threads "  + args.threads +
# todo: confirm that 1000 for this parameter is ok for deep sequencing data
# todo: It might be too low...
#" --mad " + str(args.dp) +
#" --kmer " + kmers +
#" --working " + tmpdir

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
# todo: correct mem reqs?
- -Xmx20g
- -Djava.io.tmpdir=/scratch
- -jar
# todo: issue with upgrade to 2.14? 2.07 seemed to have issue.
# See notes/PrintReads_filtering_issue.sh
#- /opt/common/CentOS_6-dev/abra/2.07/abra2-2.07.jar
#- /home/johnsoni/Innovation-Pipeline/vendor_tools/abra2-2.14.jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/abra-0.92-SNAPSHOT-jar-with-dependencies.jar

requirements:
  InlineJavascriptRequirement: {}
  ShellCommandRequirement: {}
  ResourceRequirement:
    ramMin: 20000
    coresMin: 8

doc: |
  None

inputs:

  input_bams:
    type:
      type: array
      items: File
    inputBinding:
      prefix: --in
      itemSeparator: ','
    secondaryFiles:
    - ^.bai

  # Todo: Can Abra auto-delete this dir?
  # Or do we really need another intermediate Python step...?
  working_directory:
    type: string
    inputBinding:
      prefix: --working

  reference_fasta:
    type: string
    inputBinding:
      prefix: --ref

  targets:
    type: File
    inputBinding:
      prefix: --targets
      # todo: same as -tr?

  threads:
    type: int
    inputBinding:
      prefix: --threads
      # todo: same as -t?

  kmer:
    type: string
    inputBinding:
      prefix: --kmer
      shellQuote: false

  mad:
    type: int
    inputBinding:
      prefix: --mad

  out:
    type:
      type: array
      items: string
    doc: Required list of output sam or bam file (s) separated by comma
    inputBinding:
      itemSeparator: ','
      prefix: --out

outputs:

  bams:
    type: File[]
    outputBinding:
      glob: '*_abraIR.bam'
