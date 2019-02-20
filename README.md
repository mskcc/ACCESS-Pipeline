![Build Status](https://travis-ci.com/mskcc/ACCESS-Pipeline.svg?token=7e9uBYr6xqTkAeLnyoYR&branch=master)

# Getting Started

Disclaimer: Running the pipeline depends on installation of certain dependencies. Moving to docker containers is the long term solution for this. For now these tools must be previously installed:

| Tool | Version |
| --- | --- |
| GCC | 4.4.7 |
| glibc | 2.12 |
| Java 7 | jdk1.7.0_75 |
| Java 8 | jdk1.8.0_31 |
| Python (must exist in PATH)| 2.7.10 |
| R (must exist in PATH)| 3.4.2 |
| Perl (must exist in PATH)| 5.20.2 |
| Node (must exist in PATH)| v6.10.1 |
| [Trimgalore](https://github.com/FelixKrueger/TrimGalore) | v0.2.5 (also needs to have paths to fastqc and cutadapt updated manually) |
| [BWA](https://github.com/lh3/bwa) (must exist in PATH) | 0.7.15-r1140 |
| [bedtools](https://github.com/arq5x/bedtools2) (must exist in PATH) | v2.26.0 |
| [Cutadapt](http://cutadapt.readthedocs.io/en/stable/installation.html) | 1.1 | 
| [Fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) | v0.10.1 |
| [Marianas](https://github.com/juberpatel/Marianas) | 1.5 |
| [Waltz](https://github.com/juberpatel/Waltz) | 2.0 |
| [Picard](https://github.com/broadinstitute/picard) | picard-2.8.1.jar |
| Picard AddOrReplaceReadGroups | AddOrReplaceReadGroups-1.96.jar |
| Picard FixMateInformation | FixMateInformation.jar (1.96) |
| [GATK](https://github.com/broadgsa/gatk-protected) | 3.3.0 |
| [Abra](https://github.com/mozack/abra/) | abra-0.92-SNAPSHOT-jar-with-dependencies.jar |

- HG19 Reference fasta + fai
- dbSNP & Millis_100G vcf + .vcf.idx files
- [Virtualenv](https://virtualenv.pypa.io/en/stable/)

# Provenance
These CWL modules and python script originated from the [Roslin pipeline](https://github.com/mskcc/roslin-variant) at MSKCC. 

# Installation

Note: In these instructions, please replace *0.0.26* with the *latest stable version* of the pipeline (see the Releases page). 

### 1. Set up a Virtual Environment
Make virtualenv with the name of your virtual environment for this project (e.g. access_pipeline_0.0.26)

Note: If on LUNA, use the following verison of virtualenv:
```
~$ /opt/common/CentOS_6-dev/bin/current/virtualenv --python=/opt/common/CentOS_6-dev/python/python-2.7.10/bin/python ~/access_pipeline_0.0.26
~$ source ~/access_pipeline_0.0.26/bin/activate
```

### 2. Copy the latest release of the pipeline
(Make sure your virtualenv is active)
```
(access_pipeline_0.0.26) ~$ git clone https://github.com/mskcc/ACCESS-Pipeline.git --branch 0.0.26
```

### 3. Update your environment variables:
Use the following script to get LUNA-specific environment variables for Toil and ACCESS dependencies
```
(access_pipeline_0.0.26) ~$ source ~/ACCESS-Pipeline/python_tools/pipeline_kickoff/workspace_init.sh
```

### 4. Install the python tools
From within the ACCESS-Pipeline repository directory, run the following command:
```
(access_pipeline_0.0.26) ~/ACCESS-Pipeline$ python setup.py install && python setup.py clean
```

## Additional setup steps, if not on LUNA:

### 1. Copy the test data
It should be possible to use full-sized reference `fasta`, `fai`, `bwt`, `dict`, `vcf`, and `vcf.idx` files, but smaller test versions are located here on Luna:
```
(access_pipeline_0.0.26) ~$ cp -r /home/johnsoni/test_reference .
```

### 2. Update the run variables

If you are not on LUNA, you will need to contact johnsoni@mskcc.org or patelj1@mskcc.org for the latest ACCESS-specific interval lists, and get access to all of the required resources that are referenced in these files:
```
/resources/run_tools/luna.yaml

/resources/run_files/test.yaml
/resources/run_files/production.yaml

/resources/run_params/test.yaml
/resources/run_params/production.yaml
```
And then update the paths to these variables.

### 3. If on SGE, update environment variables
If you are using the SGE batch system, you will also need to set these variables for Toil:
```
export TOIL_GRIDENGINE_ARGS="-q <queue that you want to use for toil jobs>"
export TOIL_GRIDENGINE_PE="smp"
```

### 4. Install R libraries
These are used by the QC module at the end of the pipeline. You can check if these are already installed by running `library(yaml)` and `library(dplyr)` in an R session.
```
(access_pipeline_0.0.26) ~/ACCESS-Pipeline$ Rscript -e 'install.packages(c("yaml", "dplyr"), repos="http://cran.rstudio.com", lib="~/R")'
```

# Running the test pipeline
NOTE: These steps should be run from a new directory, but still while inside your virtual environment, and after sourcing the `workspace_init.sh` script. 

### 1. Create a run title file from a sample manifest
(example manifests exist in /test/test_data/...)
```
(access_pipeline_0.0.26) ~/my_TEST_run$ create_title_file_from_manifest -i ../ACCESS-Pipeline/test/test_data/umi-T_N-PanCancer/test_manifest.xls -o XX_title_file.txt
```

### 2. Create an inputs file from the title file
This step will create a file `inputs.yaml`, and pull in the run parameters (-t for test, -c for collapsing) and paths to run files from step 5.
```
(access_pipeline_0.0.26) ~/my_TEST_run$ create_inputs_from_title_file -i XX_title_file.txt -d ../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer -p TEST_run -o inputs.yaml -t
```

### 3. Run the test pipeline
To run with the CWL reference implementation (faster for testing purposes):
```
(access_pipeline_0.0.26) ~/my_TEST_run$ cwltool \
  --debug                                                     # For debug level logging
  --tmpdir-prefix ~/my_TEST_run \                             # Where to put temp directories
  --cachedir ~/my_TEST_run \                                  # Where to cache intermediate outputs (useful for restart after failure)
  ~/ACCESS-Pipeline/workflows/ACCESS_pipeline.cwl \           # The workflow *required*
  inputs.yaml                                                 # The inputs to the workflow *required*
```
Or, to run with the Toil batch system runner:
```
(access_pipeline_0.0.26) ~/my_TEST_run$ toil-cwl-runner ~/ACCESS-Pipeline/workflows/ACCESS-pipeline.cwl inputs.yaml
```

# Running a real run
NOTE: These steps should be run from a new directory, but still while inside your virtual environment, and after sourcing the `workspace_init.sh` script. 

I usually start pipeline runs from a fresh directory, with ample storage space. This is where the batch system log files will be written. However, these logs are different from the Toil log files, which will be placed alongside the pipeline outputs as specified by the `output_location` parameter. Both sets of log files can be quite large (up to ~50GB if running in debug mode on a large pool). 

Note that there are several valiation requirements when running on your own data (use the example manifests in `test/test_data` for examples):
1. The header names that are found in the sample manifest should matched with the examples in `test/test_data`
2. The sample ID's in the manifest must be matched somewhere in the paths to the fastqs and sample sheets fom the `-d` data folder
3. Each sample in the `-d` data folder must have these three files:
```
'_R1_001.fastq.gz'
'_R2_001.fastq.gz'
'SampleSheet.csv'
```
4. The i5 and i7 barcode indexes from the manifest/title_file must match what is found in the SampleSheet.csv files (i5 may be reverse-complemented depending on the machine).
5. The `sample_class` field must always be either "Tumor" or "Normal"
6. The `sample_type` field must always be either "Plasma" or "Buffy Coat"

Certain validation requirements can be skipped by using the `-f` parameter in the pipeline kickoff step.

## Example:

### 1. Use the inputs generation scripts

These are the same as when used for running a test with `cwltool` or `toil-cwl-runner`. Note that if there are multiple lanes in the manifest the first script will create multiple title files on a per-lane basis.
```
(access_pipeline_0.0.26) ~/my_REAL_run$ create_title_file_from_manifest -i ~/manifests/ES_manifest.xlsx -o ./ES_title_file.txt
(access_pipeline_0.0.26) ~/my_REAL_run$ create_inputs_from_title_file -i lane-5_ES_title_file.txt -d /home/johnsoni/Data/JAX_0149_AHT3N3BBXX/Project_05500_ES -p 5500-ES_lane-5 -o inputs_lane_5.yaml
```

### 2. Use the pipeline runner/submit scripts

Note that we use `pipeline_submit` here to submit both the leader job as well as the worker jobs to the cluster.

Right now the only supported options for the `--batch-system` parameter are `lsf` and `singleMachine`.

```
(access_pipeline_0.0.26) ~/my_REAL_run$ pipeline_submit \
--project_name EJ_4-27_MarkDuplicatesTest \
--output_location /home/johnsoni/projects/EJ_4-27_MarkDuplicatesTest \
--inputs_file ./inputs.yaml \
--workflow ~/ACCESS-Pipeline/workflows/ACCESS_pipeline.cwl \
--batch_system lsf
```

Or alternatively, use `pipeline_runner` to make use of the `gridEngine`, `mesos`, `htcondor` or `slurm` options. 

This script can be run in the background with `&`, and will make use of worker nodes for the jobs themselves.

```
(access_pipeline_0.0.26) ~/my_REAL_run$ pipeline_runner \
--output_location /home/projects/EJ_4-27_MarkDuplicatesTest \
--inputs_file ./inputs.yaml \
--workflow ~/ACCESS-Pipeline/workflows/ACCESS_pipeline.cwl \
--batch_system gridEngine
```
This will create the output directory (or restart a failed run in that output directory for `--restart`), and start the workflow using SGE.

### 3. Cleanup the output files
There is a script included to create symlinks to the output bams and delete unnecessary output folders left behind by Toil
```
(access_pipeline_0.0.26) ~$ pipeline_postprocessing -d <path/to/outputs>
```

### 4. Test the output files
There is a script included to check that the correct samples are paired in the correct folders, and that expected files are present in the final output directory.
```
(access_pipeline_0.0.26) ~$ python -m python_tools.test.test_pipeline_outputs -o <path_to_outputs> -l debug
```

# Issues
Bug reports and questions are helpful, please report any issues, comments, or concerns to the [issues page](https://github.com/mskcc/Innovation-Pipeline/issues)

# Documentation
Additional information can be found in the [Wiki](https://github.com/mskcc/access-pipeline/wiki), including tips for CWL and Toil, and working with ACCESS log files.
