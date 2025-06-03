# Creating ACCESS V1 Environment on IRIS

Running this pipeline on the IRIS cluster is done out of necessity. The only goal of this branch is to provide the bare minimum instruction for running XSV1 on IRIS. The bare minimum updates have been made to achieve this goal. This repository was never meant to be run outside of the JUNO cluster and should have been containerized long ago. XSV2 is also now the primary XS workflow. 

Running the pipeline depends on installation of certain dependencies. These tools must installed:

External Dependencies
| Tool | Version | Path | Notes
| --- | --- |
| GCC | gcc (GCC) 8.5.0 20210514 (Red Hat 8.5.0-22) | /usr/bin/gcc | installed by BioTeam
| Java 7 | jdk1.7.0_80 | /admin/software/migration-testing/java/jdk1.7.0_80/bin/java | installed by BioTeam
| Java 8 | jdk1.8.0_31 | /admin/software/migration-testing/java/jdk1.8.0_31/bin/java | installed by BioTeam
| Node (must exist in PATH)| v10.24.0 | /usr/bin/node
| [Trimgalore](https://github.com/FelixKrueger/TrimGalore) | v0.2.5 (also needs to have paths to fastqc and cutadapt updated manually) | /home/buehlere/access_tools/trim_galore/Trim_Galore_v0.2.5/trim_galore | manually copied from juno, version is no longer available on GitHub
| [Marianas](https://github.com/juberpatel/Marianas) | 1.8.0 | /home/buehlere/access_tools/Marianas-1.8.0.jar | Version is still available on Github, but manually copied from Juno. I was having trouble with the install. It still might be possible to build from source.
| [Waltz](https://github.com/juberpatel/Waltz) | 2.0 | /home/buehlere/access_tools/waltz/versions/v2.0.0/Waltz-2.0.jar | manually copied from juno, version is no longer available on GitHub.
| [Picard] fixmate (https://github.com/broadinstitute/picard) | picard-2.8.1.jar | /home/buehlere/access_tools/picard/versions/v2.8.1/picard.jar | Version is still available on Github. However, I manually copied from juno as I'm not sure why the jars are separated out into sub-commands. This doesn't seem to be how picard is compiled currently. This is likely a quirk unique to the XSV1 pipeline. 
| Picard AddOrReplaceReadGroups | AddOrReplaceReadGroups-1.96.jar | /home/buehlere/access_tools/picard/versions/v1.96/picard-tools-1.96/AddOrReplaceReadGroups.jar | Version is still available on Github. However, I manually copied from juno as I'm not sure why the jars are separated out into sub-commands. This doesn't seem to be how picard is compiled currently. This is likely a quirk unique to the XSV1 pipeline.,
| [GATK](https://github.com/broadgsa/gatk-protected) | 3.3.0 | /home/buehlere/access_tools/gatk/GenomeAnalysisTK-3.3-0/GenomeAnalysisTK.jar | Version is still available on Github, but manually copied from Juno. I was having trouble with the install. It still might be possible to build from source.
| [Abra](https://github.com/mozack/abra2) | 2.17 | /home/buehlere/access_tools/abra2/abra2-2.17/abra2-2.17.jar | Version is still available on Github, but manually copied from Juno. I was having trouble with the install. It still might be possible to build from source.

Note: BWA, bedtools, cutadapt, fastqc, R and python were previously listed as external dependencies. These have now been added to the `environment.yaml`.

# Installation

### 1. Copy the latest release of the pipeline
```
$ git clone https://github.com/mskcc/ACCESS-Pipeline.git --branch IRIS/XS_V1
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
  --jobStore /scratch/test01/buehlere/jobstore_13102_T \
  --workDir /scratch/test01/buehlere/workdir \
  --outdir /data1/test01/cci/Project_13102_T \
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
  /home/buehlere/ACCESS-Pipeline/workflows/ACCESS_pipeline.cwl \
  /home/buehlere/access_tests/v1/Project_13102_T/input.json
```

I recommend generating the `input.json` using Voyager: https://github.com/mskcc/beagle/tree/master/runner/operator/access/v1_0_0. 

However, you can still do this yourself by following these steps: 

### 1. Create a run title file from a sample manifest

(example manifests exist in /test/test_data/...)
```
(ACCESS) $ create_title_file_from_manifest \
  -i ~/ACCESS-Pipeline/test/test_data/umi-T_N-PanCancer/test_manifest.xlsx \
  -o test_title_file.txt
```

### 2. Create an inputs file from the title file

```
(ACCESS) $ create_inputs_from_title_file \
  -i test_title_file.txt \
  -d ~/ACCESS-Pipeline/test/test_data/umi-T_N-PanCancer \
  -p TEST_run \
  -o inputs.yaml \
  -t \
  -f
```
This step will create a file `inputs.yaml`, and pull in the run parameters (-t for test, -c for collapsing) and paths to run files from step 5. I recommend seeing the original `README.md` for additional guidance.
