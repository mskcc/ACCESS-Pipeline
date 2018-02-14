#!/bin/bash

../../../pipeline-runner.sh \
    test_fulcrum_annotatebamwithumis \
    ../../../tools/fulcrum/AnnotateBamWithUmis.cwl \
    inputs.yaml
