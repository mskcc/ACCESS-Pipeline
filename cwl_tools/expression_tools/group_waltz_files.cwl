#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: ExpressionTool

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 2000

inputs:

  covered_regions: File
  fragment_sizes: File
  read_counts: File
  pileup: File
  pileup_without_duplicates: File
  intervals: File
  intervals_without_duplicates: File

outputs:
  waltz_files:
    type:
      type: array
      items: File

expression: '${
  var output_files = [];

  output_files.push(inputs.covered_regions);
  output_files.push(inputs.fragment_sizes);
  output_files.push(inputs.read_counts);
  output_files.push(inputs.pileup);
  output_files.push(inputs.pileup_without_duplicates);
  output_files.push(inputs.intervals);
  output_files.push(inputs.intervals_without_duplicates);

  return { "waltz_files": output_files }
}'
