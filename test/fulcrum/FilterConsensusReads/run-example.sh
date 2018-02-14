#!/bin/bash

../../../pipeline-runner.sh \
    test_fulcrum_filterconsensusreads \
    ../../../tools/fulcrum/FilterConsensusReads.cwl \
    inputs.yaml
