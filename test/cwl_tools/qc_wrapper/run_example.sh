#!/bin/bash


cwltool \
    ./cwl_tools/python/innovation-qc.cwl \
    test/cwl_tools/qc_wrapper/inputs.yaml
