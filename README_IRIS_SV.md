# Getting Started

This README assumes the conda environment from  `README_IRIS_BAMS.md` has been completed.

Disclaimer: Running the pipeline depends on installation of certain dependencies. Moving to docker containers is the long term solution for this. For now these tools must be previously installed:

External Dependencies
| Tool | Version | Path | Notes
| --- | --- |
| [ACCESS_SV](https://github.com/mskcc/ACCESS_SV) | master | /home/buehlere/access_tools/ACCESS_SV/ | cloned from source using git clone --recursive https://github.com/mskcc/ACCESS_SV.git. Note that recursive must be used as the repository contains git lfs and submodules.
| [iANNOTATESV](https://github.com/rhshah/iAnnotateSV/tree/master) | index_fix_py2 | https://github.com/rhshah/iAnnotateSV/tree/feature/index_fix_py2 | Note this is a submodule of ACCESS_SV and should be added using `git clone --recursive https://github.com/mskcc/ACCESS_SV.git`
| [gitlfs](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) | any | NA

Notes here are the location of the git lfs directories mentioned above:
- `/home/buehlere/access_tools/ACCESS_SV/iAnnotateSV/iAnnotateSV/data/`
- `/home/buehlere/access_tools/ACCESS_SV/`

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
  --jobStore /scratch/test01/buehlere/store/sv \
  --workDir /scratch/test01/buehlere/work/sv \
  --outdir /data1/test01/cci/Project_13102_T_SV \
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
  /home/buehlere/ACCESS-Pipeline/workflows/subworkflows/manta.cwl \
  /home/buehlere/access_tests/v1/Project_13102_T_SV/input.json
```

