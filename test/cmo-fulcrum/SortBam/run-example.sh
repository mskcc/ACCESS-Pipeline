#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w cmo-fulcrum.SortBam/0.0.0/cmo-fulcrum.SortBam.cwl \
    -i inputs.yaml \
    -b lsf
