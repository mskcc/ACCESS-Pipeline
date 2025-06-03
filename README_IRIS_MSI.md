# Getting Started

This README assumes the conda environment from  `README_IRIS_BAMS.md` has been completed.

Disclaimer: Running the pipeline depends on installation of certain dependencies. Moving to docker containers is the long term solution for this. For now these tools must be previously installed:

External Dependencies
| Tool | Version | Path | Notes
| --- | --- |
| [MSISENSOR](https://github.com/ding-lab/msisensor/tree/0.2) | 0.2 | /home/buehlere/access_tools/msisensor/msisensor | cloned from source using

msisensor needs to be available on path: `export PATH=/home/buehlere/access_tools/msisensor:$PATH`

### 1. Activate Conda Virtual Environment
```
$ conda activate ACCESS
```

# Running the pipeline

### 3. Run the pipeline
To run with the CWL reference implementation (faster for testing purposes):
```
export TOIL_SLURM_ARGS="--account=test01 --partition=test01 --time=0-6:00:00"

toil-cwl-runner \
  --maxMemory 900G \
  --maxDisk 800G \
  --maxCores 24 \
  --defaultCores 10 \
  --tmpdir-prefix /tmp \
  --jobStore /scratch/test01/buehlere/store/msi \
  --workDir /scratch/test01/buehlere/work/msi \
  --outdir /data1/test01/cci/Project_13102_T_MSI \
  --cleanWorkDir onSuccess \
  --clean onSuccess \
  --logLevel DEBUG \
  --no-container \
  --batchSystem slurm \
  --logFile slurm.log \
  --preserve-environment PATH TMPDIR PWD _JAVA_OPTIONS PYTHONPATH TEMP \
  --disableChaining \
  --runCwlInternalJobsOnWorkers \
  --maxLocalJobs 500 \
  --retryCount 2 \
  /home/buehlere/ACCESS-Pipeline/workflows/subworkflows/msi.cwl \
  /home/buehlere/access_tests/v1/Project_13102_T_MSI/input.json
```

