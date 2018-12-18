cwlVersion: v1.0

class: CommandLineTool

arguments:
- $(inputs.java)
- -Xmx60g
- -Djava.io.tmpdir=$(inputs.working_directory.path)
- -jar
- $(inputs.abra)

requirements:
  InlineJavascriptRequirement: {}
  ResourceRequirement:
    ramMin: 60000
    coresMin: 8
    outdirMax: 90000

# Todo: It would be nice to have this
# but unfortunately PATH is not a defined
# variable in the CWL parsing environment.
# For now we rely on including BWA at the beginning
# of our PATH before starting the run
#
#  EnvVarRequirement:
#    envDef:
#      PATH: $(inputs.bwa + ':' + PATH)

inputs:
  java: string
  abra: string

  input_bams:
    type:
      type: array
      items: File
    inputBinding:
      prefix: --in
      itemSeparator: ','
    secondaryFiles:
    - ^.bai

  patient_id:
    type: string

  working_directory:
    type: Directory
    inputBinding:
      prefix: --tmpdir

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
    type: string
    inputBinding:
      prefix: --kmer

  mad:
    type: int
    inputBinding:
      prefix: --mad

  out:
    type:
      type: array
      items: string
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
