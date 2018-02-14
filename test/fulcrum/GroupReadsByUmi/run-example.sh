#!/bin/bash

../../../pipeline-runner.sh \
    test_fulcrum_groupreadsbyumi \
    ../../../tools/fulcrum/GroupReadsByUmi.cwl \
    inputs.yaml
