cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_tools/schemas.yaml
      - $import: ../../resources/run_params/schemas/find_covered_intervals.yaml
      - $import: ../../resources/run_params/schemas/abra.yaml
      - $import: ../../resources/run_params/schemas/fix_mate_information.yaml

inputs:
  tmp_dir: string
  run_tools: ../../resources/run_tools/schemas.yaml#run_tools

  bams:
    type: File[]
    secondaryFiles:
      - ^.bai

  reference_fasta: string
  patient_id: string

  find_covered_intervals__params: ../../resources/run_params/schemas/find_covered_intervals.yaml#find_covered_intervals__params
  abra__params: ../../resources/run_params/schemas/abra.yaml#abra__params
  fix_mate_information__params: ../../resources/run_params/schemas/fix_mate_information.yaml#fix_mate_information__params

  fci__basq_fix: boolean?

outputs:

  ir_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
    outputSource: parallel_fixmate/bams

  covint_list:
    type: File
    outputSource: find_covered_intervals/fci_list

  covint_bed:
    type: File
    outputSource: list2bed/output_file

steps:

  find_covered_intervals:
    run: ../../cwl_tools/gatk/FindCoveredIntervals.cwl
    in:
      tmp_dir: tmp_dir
      run_tools: run_tools
      params: find_covered_intervals__params
      java:
        valueFrom: $(inputs.run_tools.java_7)
      gatk:
        valueFrom: $(inputs.run_tools.gatk_path)

      bams: bams
      patient_id: patient_id
      reference_sequence: reference_fasta

      min_base_quality:
        valueFrom: $(inputs.params.minbq)
      min_mapping_quality:
        valueFrom: $(inputs.params.minmq)
      coverage_threshold:
        valueFrom: $(inputs.params.cov)
      read_filters:
        valueFrom: $(inputs.params.rf)
      intervals:
        valueFrom: ${return inputs.params.intervals ? inputs.params.intervals : null}
      ignore_misencoded_base_qualities: fci__basq_fix
      out:
        valueFrom: ${return inputs.patient_id + '.fci.list'}
    out: [fci_list]

  list2bed:
    run: ../../cwl_tools/python/list2bed.cwl
    in:
      input_file: find_covered_intervals/fci_list
      output_filename:
        valueFrom: ${return inputs.input_file.basename.replace('.list', '.bed.srt')}
    out: [output_file]

  make_abra_tmp_dir:
    run: ../../cwl_tools/python/make_directory.cwl
    in: []
    out: [empty_dir]

  abra:
    run: ../../cwl_tools/abra/abra.cwl
    in:
      run_tools: run_tools
      params: abra__params
      java:
        valueFrom: $(inputs.run_tools.java_8)
      abra:
        valueFrom: $(inputs.run_tools.abra_path)
      input_bams: bams
      targets: list2bed/output_file
      patient_id: patient_id
      reference_fasta: reference_fasta

      kmer:
        valueFrom: $(inputs.params.kmers)
      mad:
        valueFrom: $(inputs.params.mad)
      threads:
        valueFrom: $(12)
      working_directory: make_abra_tmp_dir/empty_dir
      out:
        valueFrom: $(inputs.input_bams.map(function(b){return b.basename.replace('.bam', '_IR.bam')}))
    out:
      [bams]

  parallel_fixmate:
    in:
      run_tools: run_tools
      params: fix_mate_information__params

      java:
        valueFrom: $(inputs.run_tools.java_7)
      fix_mate_information:
        valueFrom: $(inputs.run_tools.fx_path)
      bam: abra/bams
      tmp_dir: tmp_dir

      sort_order:
        valueFrom: $(inputs.params.sort_order)
      create_index:
        valueFrom: $(inputs.params.create_index)
      compression_level:
        valueFrom: $(inputs.params.compression_level)
      validation_stringency:
        valueFrom: $(inputs.params.validation_stringency)

    out: [bams]
    scatter: [bam]
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
        java: string
        fix_mate_information: string
        bam: File
        tmp_dir: string
        sort_order: string
        create_index: boolean
        compression_level: int
        validation_stringency: string
      outputs:
        bams:
          type: File
          outputSource: picard_fixmate_information/bam
      steps:
        picard_fixmate_information:
          run: ../../cwl_tools/picard/FixMateInformation.cwl
          in:
            java: java
            fix_mate_information: fix_mate_information
            input_bam: bam
            tmp_dir: tmp_dir
            sort_order: sort_order
            create_index: create_index
            compression_level: compression_level
            validation_stringency: validation_stringency
          out: [bam]
