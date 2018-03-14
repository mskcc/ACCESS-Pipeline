#!/bin/bash


output_dir=$1

DD=$(date +%d)
MM=$(date +%m)
project="ES_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

# Run test pipeline
python pipeline-submit.py \
    --project_name=${project} \
    --workflow=../workflows/innovation_pipeline.cwl \
    --inputs_file=inputs-ES.yaml \
    --output_location=${output_directory} \
    --batch_system=lsf
