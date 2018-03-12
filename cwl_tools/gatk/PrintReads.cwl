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
  doap:revision: 0.0.0
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

#$QSUB -q $queue -V -wd $outdir -N PrintBQSR.$id.$$ -o PrintBQSR.$id.$$.stdout -e PrintBQSR.$id.$$.stderr -l h_vmem=8G,virtual_free=8G -pe smp 3 -b y
#
#$JAVA_1_7
#-Xmx4g
#-Djava.io.tmpdir=$TMPDIR
#-jar $GATK
#-T PrintReads
#-I $file
#-R $Reference
#-baq RECALCULATE
#-BQSR $BQSRtable
#-nct 8
#-EOQ
#-o $outFilename

#/opt/common/CentOS_6/java/jdk1.7.0_75/bin/java
#-Xmx4g
#-Djava.io.tmpdir=/ifs/work/scratch/
#-jar /opt/common/CentOS_6/gatk/GenomeAnalysisTK-3.3-0/GenomeAnalysisTK.jar
#-T PrintReads
#-I MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX.bam
#-R /ifs/depot/resources/dmp/data/pubdata/hg-fasta/VERSIONS/hg19/Homo_sapiens_assembly19.fasta
#-baq RECALCULATE
#-BQSR MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_recalReport.grp
# todo: didn't see these next two params in the Roslin cwl wrapper:
#-nct 8
#-EOQ
#-o MSK-L-009-bc-IGO-05500-DY-6_bc209_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam

baseCommand:
- /opt/common/CentOS_6/java/jdk1.8.0_25/bin/java

arguments:
- -Xmx20g
- -Djava.io.tmpdir=/scratch
- -jar
- /home/johnsoni/Innovation-Pipeline/vendor_tools/GenomeAnalysisTK.jar
- -T
- PrintReads

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 20000
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
