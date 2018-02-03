#!/bin/bash

pipeline_name_version="variant/1.3.1"

cmd="roslin-runner.sh \
    -v variant/1.3.1 \
    -w innovation-merge-directories/0.0.0/innovation-merge-directories.cwl \
    -i /home/johnsoni/roslin/setup/examples/innovation/inputs-merge.yaml \
    -b lsf \
    -o /ifs/work/bergerm1/Innovation/sandbox/ian/outputs-merge"

echo $cmd

eval $cmd