#!/usr/bin/env/cwl-runner

cwlVersion: v1.0

class: ExpressionTool
requirements:
  - class: InlineJavascriptRequirement

inputs:

  covered_regions:
    type: File

  fragment_sizes:
    type: File

  read_counts:
    type: File

  pileup:
    type: File

  pileup_without_duplicates:
    type: File

  intervals:
    type: File

  intervals_without_duplicates:
    type: File

outputs:
  waltz_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: '*'

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
