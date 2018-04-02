#!/bin/bash


output_dir=$1

D=$(date +%d)
m=$(date +%m)
M=$(date +%M)
project="EF_${m}-${D}_${M}"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

python ../pipeline-submit.py \
    --project_name=${project} \
    --workflow=../../workflows/standard_pipeline.cwl \
    --inputs_file=inputs.yaml \
    --output_location=${output_directory} \
    --batch_system=lsf
