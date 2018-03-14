#!/bin/bash


output_dir=$1

DD=$(date +%d)
MM=$(date +%m)
project="DY_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

python ../pipeline-submit.py \
    --project_name=${project} \
    --workflow=../../workflows/innovation_pipeline.cwl \
    --inputs_file=inputs.yaml \
    --output_location=${output_directory} \
    --batch_system=lsf
