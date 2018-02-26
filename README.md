### Innovation Pipeline

[![Build Status](https://travis-ci.org/mskcc/Innovation-Pipeline.svg?branch=master)](https://travis-ci.org/mskcc/Innovation-Pipeline)

Usage:

(Note: These steps are preliminary, and are waiting on consolidation of the following dependencies)

- Innovation-QC
- CMO (to be removed)
- Paths to installed versions of:
  - Fulcrum
  - Marianas
  - Waltz
  - BWA
  - Picard
  - Samtools
- HG19 Reference fasta + fai

```
# Set up a Virtual Environment
virtualenv ~/my-virtual-env
source ~/my-virtual-env/bin/activate

# Clone the QC module
git clone https://github.com/mskcc/Innovation-QC.git
cd Innovation-QC
python setup.py install

# Install Toil CWL-runner
pip install toil'[cwl]'==3.14.0

# Run the test pipeline
toil-cwl-runner workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
<or>
test/run-pipeline-test.sh <output_dir>
```
