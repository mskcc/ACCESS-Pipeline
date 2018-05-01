### Innovation Pipeline

# Getting Started

Note: These steps are preliminary, and are waiting on consolidation of certain dependencies. Moving to docker containers is the long term solution for this. For now these additional dependencies must be explicitly installed:

| tool | version |
| --- | --- |
| [Trimgalore](https://github.com/FelixKrueger/TrimGalore) | v0.2.5 (also needs to have paths to fastqc and cutadapt updated manually)|
| Java 7 | jdk1.7.0_75 |
| Java 8 | jdk1.8.0_31 |
| Python | 2.7.10 |
| R | 3.4.2 |
| Perl | 5.20.2 |
| [BWA](https://github.com/lh3/bwa) (must exist in PATH) | 0.7.15-r1140 |
| [bedtools](https://github.com/arq5x/bedtools2) (must exist in PATH) | v2.26.0 |
| [Marianas](https://github.com/juberpatel/Marianas) | 1.5 |
| [Waltz](https://github.com/juberpatel/Waltz) | 2.0 |
| [Picard](https://github.com/broadinstitute/picard) | picard-2.8.1.jar |
| Picard AddOrReplaceReadGroups | AddOrReplaceReadGroups-1.96.jar |
| Picard FixMateInformation | FixMateInformation.jar (1.96) |
| [GATK](https://github.com/broadgsa/gatk-protected) | 3.3.0 |
| [Abra](https://github.com/mozack/abra/) | abra-0.92-SNAPSHOT-jar-with-dependencies.jar |

- HG19 Reference fasta + fai
- dbSNP & Millis_100G vcf + .vcf.idx files

# Installation

### 1. Set up a Virtual Environment
Make virtualenv with the name of your virtual environment for this project (e.g. innovation_pipeline)
```
~$ virtualenv ~/innovation_pipeline
~$ source ~/innovation_pipeline/bin/activate
```

### 2. Copy the latest release of the pipeline and Install the python tools
(Make sure your virtualenv is active)
```
(innovation_pipeline) ~$ git clone https://github.com/mskcc/Innovation-Pipeline.git --branch 0.0.3
(innovation_pipeline) ~$ cd Innovation-Pipeline
```

### 3. Update the paths to the tool resources and run files
There are several combinations of resource files to edit, to support different environments and run types. The minimal changes that will have to be made to run the tests include:
```
/resources/run_files/test.yaml
/resources/run_files/test__collapsing.yaml
/resources/run_tools/luna.yaml
/resources/run_params/test.yaml
/resources/run_params/test__collapsing.yaml
```

### 4. Include the paths to BWA and Bedtools as the first entries in your path:
Abra and pybedtools will use these versions of BWA & bedtools implicitly.  This is not ideal, but remains the only solution for now unless we move to Docker containers
```
PATH="/usr/bin/bwa:$PATH"
PATH="/usr/bin/bedtools:$PATH"
```

### 5. Set the root directory of the project
(found in `/python_tools/constants.py`)
```
ROOT_DIR = '/home/johnsoni/Innovation-Pipeline'
```

### 6. Install the python tools
```
(innovation_pipeline) ~/Innovation-Pipeline$ python setup.py install
```

# Running the test pipeline

I usually run the pipelines from a separate directory, with ample storage space. Even though the pipelines outputs directory can be specified for the runs, even the log files can be quite large (up to ~50GB if running in debug mode).

### 1. Create a run title file from a sample manifest
(example manifests exist in /test/test_data/...)
```
(innovation_pipeline) ~/PIPELINE_RUNS$ create_title_file_from_manifest -i Innovation_Pipeline/test/test_data/umi-T_N/manifest.xls -o ./title_file.txt
```

### 2. Create an inputs file from the title file
This step will create a file `inputs.yaml`, and pull in the run parameters (-t for test, -c for collapsing) and paths to run files from step 5.
```
(innovation_pipeline) ~/PIPELINE_RUNS$ create_inputs_from_title_file -i ./test_title_file.txt -d Innovation-Pipeline/test/test-data/umi-T_N -t -c
```

### 3. Run the test pipeline
To run with the CWL reference implementation (faster for testing purposes):
```
(innovation_pipeline) ~/PIPELINE_RUNS$ cwltool ~/Innovation-Pipeline/workflows/standard_pipeline.cwl inputs.yaml
```
To run with Toil batch system runner:
```
(innovation_pipeline) ~/PIPELINE_RUNS$ toil-cwl-runner  ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
```
or use:
```
(innovation_pipeline) ~/PIPELINE_RUNS$ test/run-pipeline-test.sh ~/output_dir
```
Have a look inside `pipeline_runner.sh` to see some useful arguments for Toil & cwltool

# Running a real run
The same steps for testing can be used for a real run.

Note that there are several requirements when running on your own data:
1. The fields that are found in the sample manifest should matched with the examples in `test/test_data`
2. The sample ID's in the manifest must be matched somewhere in the fastq file names fom the `-d` data folder
3. The sample ID's in the manifest must be matched somewhere in the path to the SampleSheet.csv files
4. The `SAMPLE_CLASS` column of the manifest must consist of the values either "Tumor" or "Normal"
5. Each "Tumor" sample must have at least one associated "Normal" sample
6. Each sample folder in the `-d` data folder must have these three files:
```
'_R1_001.fastq.gz'
'_R2_001.fastq.gz'
'SampleSheet.csv'
```
### Example:
Note that we use `pipeline_submit` here to submit both the leader job as well as the worker jobs to the cluster.

Right now the only supported options for the `--batch-system` parameter are `lsf` and `singleMachine`.

Please use `pipeline_runner` to make use of the `gridEngine`, `mesos`, `htcondor` or `slurm` options. This script can be run in the background with `&`, and will make use of worker nodes for the jobs themselves.
```
(innovation_pipeline) ~/PIPELINE_RUNS$ create_title_file_from_manifest -i ./EJ_manifest.xlsx -o ./EJ_title_file.txt
(innovation_pipeline) ~/PIPELINE_RUNS$ create_inputs_from_title_file -i ./EJ_title_file.txt -d ~/data/DY_data -t -c
```
```
(innovation_pipeline) ~/PIPELINE_RUNS$ pipeline_submit \
>   --project_name EJ_4-27_MarkDuplicatesTest \
>   --output_location /ifs/work/bergerm1/Innovation/sandbox/ian \
>   --inputs_file ./inputs.yaml \
>   --workflow ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
>   --batch_system lsf
```
or for other job schedulers:
```
(innovation_pipeline) ~/PIPELINE_RUNS$ pipeline_runner \
>   --project_name EJ_4-27_MarkDuplicatesTest \
>   --output_location /ifs/work/bergerm1/Innovation/sandbox/ian \
>   --inputs_file ./inputs.yaml \
>   --workflow ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
>   --batch_system gridEngine \
>   --job_store_uuid some_random_uuid
```

# Issues
Bug reports and questions are helpful, please report any issues, comments, or concerns to the [issues page](https://github.com/mskcc/Innovation-Pipeline/issues)
