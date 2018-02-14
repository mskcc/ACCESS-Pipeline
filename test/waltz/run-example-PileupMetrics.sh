#!/bin/bash

../../pipeline-runner.sh \
    test_waltz_pileupmetrics \
    ../../../tools/waltz/PileupMetrics.cwl \
    inputs.yaml
