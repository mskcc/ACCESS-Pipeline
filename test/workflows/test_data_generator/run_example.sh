#!/bin/bash


output_dir=$1

D=$(date +%d)
m=$(date +%m)
H=$(date +%H)
M=$(date +%M)
project="tdg_${m}-${D}_${H}-${M}"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

pipeline_submit \
    --project_name=${project} \
    --workflow=../../../workflows/test_data_generator.cwl \
    --inputs_file=inputs.yaml \
    --output_location=${output_directory} \
    --batch_system=lsf
