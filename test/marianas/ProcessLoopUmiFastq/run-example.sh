#!/bin/bash

../../../pipeline-runner.sh \
    test_marianas_processumifastq \
    ../../../tools/marianas/ProcessLoopUmiFastq.cwl \
    inputs.yaml
