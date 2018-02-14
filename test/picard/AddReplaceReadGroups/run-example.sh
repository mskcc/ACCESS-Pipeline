#!/bin/bash

../../../pipeline-runner.sh \
    test_picard_addreplacereadgroups \
    ../../../tools/picard/AddOrReplaceReadGroups/1.96/AddOrReplaceReadGroups.cwl \
    inputs.yaml
