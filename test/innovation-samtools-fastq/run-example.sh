#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation-map-read-names-to-umis/0.0.0/innovation-map-read-names-to-umis.cwl \
    -i inputs.yaml \
    -b lsf
