#!/bin/bash

../../../pipeline-runner.sh \
    test_fulcrum_sortbam \
    ../../../tools/fulcrum/SortBam.cwl \
    inputs.yaml
