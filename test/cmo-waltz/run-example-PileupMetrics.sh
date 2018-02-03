#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w cmo-waltz.PileupMetrics/0.0.0/cmo-waltz.PileupMetrics.cwl \
    -i inputs-PileupMetrics.yaml \
    -b lsf
