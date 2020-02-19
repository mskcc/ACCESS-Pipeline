cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx50g
- -Djava.io.tmpdir=$(runtime.tmpdir)
- -jar
- $(inputs.abra)
- prefix: --tmpdir
  valueFrom: $(runtime.tmpdir)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 30000
    coresMin: 12
    outdirMax: 120000

inputs:
  java: string
  abra: string

  patient_id: string

  input_bams:
    type: File[]
    inputBinding:
      prefix: --in
      itemSeparator: ','
    secondaryFiles:
    - ^.bai

  reference_fasta:
    type: string
    inputBinding:
      prefix: --ref

  targets:
    type: File
    inputBinding:
      prefix: --targets

  threads:
    type: int
    inputBinding:
      prefix: --threads

  kmer:
    type: string?
    inputBinding:
      prefix: --kmer

  mad:
    type: int
    inputBinding:
      prefix: --mad

  sc:
    type: string
    inputBinding:
      prefix: --sc

  mmr:
    type: float
    inputBinding:
      prefix: --mmr

  sga:
    type: string
    inputBinding:
      prefix: --sga

  ca:
    type: string
    inputBinding:
      prefix: --ca

  ws:
    type: string
    inputBinding:
      prefix: --ws

  index:
    type: boolean
    inputBinding:
      prefix: --index

  cons:
    type: boolean
    inputBinding:
      prefix: --cons

  out:
    type: string[]
    inputBinding:
      itemSeparator: ','
      prefix: --out

outputs:

  bams:
    type: File[]
    outputBinding:
      # Todo: Only specify this glob string in one place:
      glob: '*_IR.bam'

      # Here we use an expression to make sure that bams come out of abra the same way that they went in,
      # regardless of their initial lexicographic order.
      #
      # `glob` on its own may change the order of the bams if they were not sorted lexicographically initially.
      outputEval: |
        ${
          var sorted_output_bams = [];

          inputs.out.forEach(function(output_bam_filename) {
            self.forEach(function(realigned_bam) {
              if (output_bam_filename === realigned_bam.basename) {

                sorted_output_bams.push(realigned_bam);

              }
            });
          });

          return sorted_output_bams
        }
