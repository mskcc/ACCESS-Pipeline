#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w cmo-waltz.CountReads/0.0.0/cmo-waltz.CountReads.cwl \
    -i inputs-CountReads.yaml \
    -b lsf
