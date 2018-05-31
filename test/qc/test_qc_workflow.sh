#!/usr/bin/env bash

source /Users/johnsoni/Desktop/virtualenvs/test12/bin/activate
export PATH=$PATH:/usr/local/bin

toil-cwl-runner \
    /Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/python/innovation-qc.cwl \
    /Users/johnsoni/Desktop/code/Innovation-Pipeline/test/qc/inputs.yaml
