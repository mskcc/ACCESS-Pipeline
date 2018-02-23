#!/bin/bash

../../../pipeline-runner.sh \
    test_picard_markduplicates \
    ../../../cwl_tools/picard/MarkDuplicates/1.96/MarkDuplicates.cwl \
    inputs.yaml
