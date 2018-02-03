#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation-extract-read-names/0.0.0/innovation-extract-read-names.cwl \
    -i inputs.yaml \
    -b lsf
