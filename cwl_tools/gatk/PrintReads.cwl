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
  doap:name: gatk.PrintReads
  doap:revision: 3.3-0
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
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
- -Xmx4g
- -Djava.io.tmpdir=/ifs/work/scratch/
- -jar
# Todo: consolidate?
- /opt/common/CentOS_6/gatk/GenomeAnalysisTK-3.3-0/GenomeAnalysisTK.jar
#- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar # v3.5
- -T
- PrintReads

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 10000
    coresMin: 8

doc: |
  None

inputs:

  out:
    type:
    - 'null'
    - string
    doc: Write output to this BAM filename instead of STDOUT
    inputBinding:
      prefix: --out

  input_file:
    type: File
    doc: Input file containing sequence data (SAM or BAM)
    inputBinding:
      prefix: --input_file

  reference_sequence:
    type: string
    inputBinding:
      prefix: --reference_sequence

  baq:
    type:
    - 'null'
    - string
    - type: array
      items: string
    doc: Type of BAQ calculation to apply in the engine (OFF| CALCULATE_AS_NECESSARY|
      RECALCULATE)
    inputBinding:
      prefix: --baq

  BQSR:
    type:
    - 'null'
    - string
    - File
    doc: Input covariates table file for on-the-fly base quality score recalibration
    inputBinding:
      prefix: --BQSR

  nct:
    type: int
    inputBinding:
      prefix: -nct

  EOQ:
    type: boolean
    inputBinding:
      prefix: -EOQ

outputs:
  out_bams:
    type: File
    secondaryFiles: [^.bai]
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out;
          return null;
        }

  out_bais:
    type: File?
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out.replace(/\.bam/,'') + ".bai";
          return null;
        }
