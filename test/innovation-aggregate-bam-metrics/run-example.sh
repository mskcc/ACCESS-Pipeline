#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation-aggregate-bam-metrics/0.0.0/innovation-aggregate-bam-metrics.cwl \
    -i inputs.yaml \
    -b lsf
