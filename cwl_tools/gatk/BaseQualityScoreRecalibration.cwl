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
  doap:name: gatk.BaseRecalibrator
  doap:revision: 0.0.0
- class: doap:Version
  doap:name: cwl-wrapper
  doap:revision: 0.0.0

dct:creator:
- class: foaf:Organization
  foaf:name: Memorial Sloan Kettering Cancer Center
  foaf:member:
  - class: foaf:Person
    foaf:name: Ian Johjnson
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

#/opt/common/CentOS_6/java/jdk1.7.0_75/bin/java
#-Xmx30g
#-Djava.io.tmpdir=/ifs/work/scratch/
#-jar /opt/common/CentOS_6/gatk/GenomeAnalysisTK-3.3-0/GenomeAnalysisTK.jar
#-T BaseRecalibrator
#-I MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX.bam
#-R /ifs/depot/resources/dmp/data/pubdata/hg-fasta/VERSIONS/hg19/Homo_sapiens_assembly19.fasta
#-knownSites /ifs/e63data/bergerm1/Resources/DMP/pubdata/dbSNP/VERSIONS/dbsnp_v137/dbsnp_137.b37.vcf
#-knownSites /ifs/e63data/bergerm1/Resources/DMP/pubdata/mills-and-1000g/VERSIONS/v20131014/Mills_and_1000G_gold_standard.indels.b37.vcf
#-rf BadCigar
#-o MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_recalReport.grp
#-nct 3

baseCommand:
- /opt/common/CentOS_6/java/jdk1.7.0_75/bin/java

arguments:
- -Xmx20g
- -Djava.io.tmpdir=/scratch
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar
- -T
- BaseRecalibrator
#- -plots

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 20000
    coresMin: 8

doc: |
  None

inputs:

  input_bam:
    type: File
    inputBinding:
      prefix: -I
    secondaryFiles:
    - ^.bai

  reference_fasta:
    type: string
    inputBinding:
      prefix: -R

  nct:
    type: int
    inputBinding:
      prefix: -nct

  rf:
    type: string
    inputBinding:
      prefix: -rf

  known_sites_1:
    type: ['null', File]
    inputBinding:
      prefix: -knownSites

  known_sites_2:
    type: ['null', File]
    inputBinding:
      prefix: -knownSites

  out:
    type:
    - 'null'
    - string
    doc: The output recalibration table file to create
    inputBinding:
      prefix: --out

outputs:

  recal_matrix:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.out)
            return inputs.out;
          return null;
        }
