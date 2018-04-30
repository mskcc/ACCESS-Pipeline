#!/usr/bin/env bash


cwltool \
    ./cwl_tools/python/aggregate_bam_metrics.cwl \
    test/cwl_tools/aggregate_bam_metrics/inputs.yaml
