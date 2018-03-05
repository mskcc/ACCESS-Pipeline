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
  doap:name: module-2
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

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  tmp_dir: string
  input_bam: File
  reference_fasta: string
  add_rg_SM: string
  abra__mad: int
  abra__kmers: string
  fix_mate_information__sort_order: string
  fix_mate_information__validation_stringency: string
  fix_mate_information__compression_level: int
  fix_mate_information__create_index: boolean
  bqsr__rf: string
  bqsr__nct: int
  bqsr__knownSites_dbSNP: File
  bqsr__knownSites_millis: File
  print_reads__nct: int
  print_reads__EOQ: boolean

#  bams:
#      type:
#          type: array
#          items: File
#      secondaryFiles:
#          - ^.bai
# todo: use our reference_fasta instead
#  genome: string
#  hapmap:
#    type: File
#    secondaryFiles:
#      - .idx
#  dbsnp:
#    type: File
#    secondaryFiles:
#      - .idx
#  indels_1000g:
#    type: File
#    secondaryFiles:
#      - .idx
#  snps_1000g:
#    type: File
#    secondaryFiles:
#      - .idx
#  rf: string[]
#  covariates: string[]
#  abra_scratch: string

# todo: doesn't seem to actually be used in FCI
#  group: string

outputs:

  outbam:
    type: File
    secondaryFiles:
      - ^.bai
    outputSource: gatk.PrintReads/out_bam

  outbai:
    type: File
    outputSource: gatk.PrintReads/out_bai

  covint_list:
    type: File
    outputSource: gatk.FindCoveredIntervals/fci_list

  covint_bed:
    type: File
    outputSource: list2bed/output_file

steps:

  gatk.FindCoveredIntervals:
    run: ../cwl_tools/gatk/FindCoveredIntervals.cwl
    in:
      input_file: input_bam
# todo: what are our groups?
      group:
        valueFrom: ${ return 'todo' }
      reference_sequence: reference_fasta
# todo: documentation for 3.3.0 of this tool? can't determine what this parameter does
#      intervals:
#        valueFrom: ${ return ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","X","Y","MT"];}
      out:
        valueFrom: ${ return inputs.group + ".fci.list"; }
    out: [fci_list]

  list2bed:
    run: ../cwl_tools/innovation-list2bed/list2bed.cwl
    in:
      input_file: gatk.FindCoveredIntervals/fci_list
      output_filename:
        valueFrom: ${ return inputs.input_file.basename.replace(".list", ".bed"); }
    out: [output_file]

  abra:
    run: ../cwl_tools/abra/abra.cwl
    in:
      working_directory: tmp_dir
      threads:
        valueFrom: ${ return 5 }
      input_bam: input_bam
      reference_fasta: reference_fasta
      targets: list2bed/output_file
      kmer: abra__kmers
      mad: abra__mad
    out:
      [bam]

  picard.FixMateInformation:
    run: ../cwl_tools/picard/FixMateInformation/1.96/FixMateInformation.cwl
    in:
      TMP_DIR: tmp_dir
      input_bam: abra/bam
      SO: fix_mate_information__sort_order
      VALIDATION_STRINGENCY: fix_mate_information__validation_stringency
      COMPRESSION_LEVEL: fix_mate_information__compression_level
      CREATE_INDEX: fix_mate_information__create_index
    out: [bam, bai]

# todo: is this supposed to run over all bams @ once?
  gatk.BaseRecalibrator:
    run: ../cwl_tools/gatk/BaseQualityScoreRecalibration.cwl
    in:
      input_bam: picard.FixMateInformation/bam
      reference_fasta: reference_fasta
      rf: bqsr__rf
      nct: bqsr__nct
      known_sites_1: bqsr__knownSites_dbSNP
      known_sites_2: bqsr__knownSites_millis
      out:
        default: "recal.matrix"
    out: [recal_matrix]

  gatk.PrintReads:
    run: ../cwl_tools/gatk/PrintReads.cwl
    in:
      nct: print_reads__nct
      EOQ: print_reads__EOQ
      reference_sequence: reference_fasta
      BQSR: gatk.BaseRecalibrator/recal_matrix
      input_file: picard.FixMateInformation/bam
#      num_cpu_threads_per_data_thread:
#        default: '5'
#      read_filter:
#        valueFrom: ${ return ["BadCigar"]; }
#      emit_original_quals:
#        valueFrom: ${ return true; }
      baq:
        valueFrom: ${ return ['RECALCULATE'];}
      out:
        valueFrom: ${ return inputs.input_file.basename.replace(".bam", "_PR.bam"); }
    out: [out_bam, out_bai]
