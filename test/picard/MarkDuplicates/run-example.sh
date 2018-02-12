#!/bin/bash

../../test-runner.sh \
    test_picard_markduplicates \
    ../../../tools/picard/MarkDuplicates/1.96/MarkDuplicates.cwl \
    inputs.yaml
