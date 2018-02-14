#!/bin/bash

../../../pipeline-runner.sh \
    test_fulcrum_callduplexconsensusreads \
    ../../../tools/fulcrum/CallDuplexConsensusReads.cwl \
    inputs.yaml
