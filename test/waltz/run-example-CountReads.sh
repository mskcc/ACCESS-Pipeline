#!/bin/bash

../../pipeline-runner.sh \
    test_waltz_countreads\
    ../../../tools/waltz/CountReads.cwl \
    inputs.yaml
