#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation-gzip-fastq/0.0.0/innovation-gzip-fastq.cwl \
    -i inputs.yaml \
    -b lsf
