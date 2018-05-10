class: ExpressionTool

inputs:
  bam: File
  sample: 'fastq_pair.yml#FastqPair'

outputs:
  bam_out: "bam.yml#Bam"

expression: >
  ${
    var bam_out={};
    bam_out['bam_file'] = inputs.bam;
    bam_out['ID'] = inputs.sample.ID;
    bam_out['LB'] = inputs.sample.LB;
    bam_out['SM'] = inputs.sample.SM;
    bam_out['PL'] = inputs.sample.PL;
    bam_out['PU'] = inputs.sample.PU;
    bam_out['CN'] = inputs.sample.CN;
    bam_out['adapter'] = inputs.sample.adapter;
    bam_out['adapter2'] = inputs.sample.adapter2;
    return {'bam_out': bam_out}
  }
