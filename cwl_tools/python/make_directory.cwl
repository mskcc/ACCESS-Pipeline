cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entryname: empty_dir
        entry: "$({class: 'Directory', listing: []})"
        writable: true

arguments: [touch, empty_dir/placeholder]

inputs: []

outputs:
  empty_dir:
    type: Directory
    outputBinding:
      glob: empty_dir
