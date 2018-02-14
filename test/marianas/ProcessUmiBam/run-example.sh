#!/bin/bash

../../../pipeline-runner.sh \
    test_marianas_processumibam \
    ../../../workflows/marianas_collapsing_workflow_duplex.cwl \
    inputs.yaml
