#!/usr/bin/env/cwl-runner

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
  doap:name: innovation-umi-trimming
  doap:revision: 0.5.0
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
- /opt/common/CentOS_6/java/jdk1.8.0_31/bin/java

arguments:
- -server
- -Xms8g
- -Xmx8g
- -cp
# todo: which Marianas for this step?
- /home/johnsoni/Innovation-Pipeline/vendor_tools/Marianas-standard.jar
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

doc: Marianas UMI Clipping module

inputs:
  fastq1:
    type: File
    inputBinding:
      position: 1

  fastq2:
    type: File

  sample_sheet:
    type: File

  umi_length:
    type: string
    inputBinding:
      position: 2

  output_project_folder:
    type: string
    inputBinding:
      position: 3

outputs:

  # todo - we need the **/ because Marianas outputs to a folder name given by the parent folder of the fastq
  processed_fastq_1:
    type: File
    outputBinding:
      glob: ${ return "**/" + inputs.fastq1.basename.split('/').pop() }

  processed_fastq_2:
    type: File
    outputBinding:
      glob: ${ return "**/" + inputs.fastq1.basename.split('/').pop().replace('_R1_', '_R2_') }

  composite_umi_frequencies:
    type: File
    outputBinding:
      glob: ${ return "**/composite-umi-frequencies.txt" }

  info:
    type: File
    outputBinding:
      glob: ${ return "**/info.txt" }

  output_sample_sheet:
    type: File
    outputBinding:
      glob: ${ return "**/SampleSheet.csv" }

  umi_frequencies:
    type: File
    outputBinding:
      glob: ${ return "**/umi-frequencies.txt" }
