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
pip install toil'[cwl]'==3.14.0
toil-cwl-runner workflows/innovation_pipelne.cwl runs/inputs_pipeline_test.yaml
```
or
```
test/run_pipeline_test.sh
```
