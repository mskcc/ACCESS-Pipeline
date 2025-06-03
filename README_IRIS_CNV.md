# Getting Started

This branch must be used when running XSV1 in the CNV pipeline. This is because XSV1 has a panel A / B concept and XSV2 doesn't. The main branch `IRIS/XS_V1` should work for running XSV1 and XSV2 in all other workflows. 

Disclaimer: Running the pipeline depends on installation of certain dependencies. Moving to docker containers is the long term solution for this. For now these tools must be previously installed:

External Dependencies
| Tool | Version | Path | Notes
| --- | --- |
| textplot.R | internal  | /home/buehlere/miniconda3/envs/ACCESS10/lib/R/library/  |  Textplot (`/home/buehlere/access_tools/textplot`) must be copied into the virtual environment `/home/buehlere/miniconda3/envs/ACCESS11/lib/R/library/` so `library(texplot)` works. I don't know where this package is from, but we need it for this pipeline.


### 1. Copy the latest release of the pipeline
```
$ git clone https://github.com/mskcc/ACCESS-Pipeline.git --branch IRIS/XS_V1_CNV
```

### 2. Conda Set-Up
Make sure conda is set up for your user:
- conda install: https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html

### 3. Run the installation
This will create a new Conda environment, and install the pipeline and its dependencies
```
$ ./setup.sh <ENV_NAME>
```
Note: I use mamba on IRIS, because the environment is quite complicated to solve, but you can edit `setup.sh` to use base conda instead.

### 6. Install Python libraries
Unfortunately, we are using a combination of Conda and Pip to get all the pipeline requirements, so you must enter the conda environment and install these libraries using pip
```
$ source activate ACCESS

(ACCESS) $ pip install .
```

# Running the test pipeline
NOTE: These steps should be run from a new directory, but still while inside your ACCESS Conda environment.

### Run the test pipeline
To run with the CWL reference implementation (faster for testing purposes):
```
export TOIL_SLURM_ARGS="--account=test01 --partition=test01 --time=0-6:00:00"

toil-cwl-runner \
  --maxMemory 900G \
  --maxDisk 800G \
  --maxCores 24 \
  --defaultCores 10 \
  --tmpdir-prefix /tmp \
  --jobStore /scratch/test01/buehlere/store/cnv \
  --workDir /scratch/test01/buehlere/work/cnv \
  --outdir /data1/test01/cci/Project_13102_T_CNV \
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
  /home/buehlere/access/v1/ACCESS-Pipeline/workflows/subworkflows/call_cnv.cwl \
  /home/buehlere/access_tests/v1/Project_13102_T_CNV/input.json

```

I recommend generating the `input.json` using Voyager: https://github.com/mskcc/beagle/tree/master/runner/operator/access/v1_0_0. 
