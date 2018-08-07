### Innovation Pipeline

# Getting Started

WARNING! These steps are preliminary, and are waiting on further pipeline validation, as well as consolidation of certain dependencies. Moving to docker containers is the long term solution for the latter. For now these additional dependencies must be explicitly installed:

| tool | version |
| --- | --- |
| [Trimgalore](https://github.com/FelixKrueger/TrimGalore) | v0.2.5 (also needs to have paths to fastqc and cutadapt updated manually)|
| Java 7 | jdk1.7.0_75 |
| Java 8 | jdk1.8.0_31 |
| Python (must exist in PATH)| 2.7.10 |
| R (must exist in PATH)| 3.4.2 |
| Perl (must exist in PATH)| 5.20.2 |
| Node (must exist in PATH)| v6.10.1 |
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

# Installation

### 1. Set up a Virtual Environment
Make virtualenv with the name of your virtual environment for this project (e.g. access_pipeline_0.0.26)
```
~$ virtualenv ~/access_pipeline_0.0.26
~$ source ~/access_pipeline_0.0.16/bin/activate
```

### 2. Copy the latest release of the pipeline
(Make sure your virtualenv is active)
```
(access_pipeline_0.0.26) ~$ git clone https://github.com/mskcc/Innovation-Pipeline.git --branch 0.0.26
(access_pipeline_0.0.26) ~$ cd Innovation-Pipeline
```
Alternatively, if you want to pull the latest development version you can use this command (requires to have the tag in the current git repo):
```
(access_pipeline_0.0.26) ~$ git clone https://github.com/mskcc/Innovation-Pipeline.git
(access_pipeline_0.0.26) ~$ git pull --tags
```

### 3. Copy the test data (optional)
It should be possible to use full-sized reference `fasta`, `fai`, `bwt`, `dict`, `vcf`, and `vcf.idx` files, but smaller test versions are located here on Luna:
```
(access_pipeline_0.0.26) ~/Innovation-Pipeline$ cp -r /home/johnsoni/test_reference .
```

### 4. Update the paths to the tool resources and run files
You will need to have your reference files and target lists available. Then provide paths to these files in the following config files. We have two sets of config files available for either running a test run or a real run, but it may be easier to simplify this to just one set. Alternatively, it is also possible to skip this step, and instead create an `inputs.yaml` file manually with paths to you own custom bedfiles. Please contact johnsoni@mskcc.org or patelj1@mskcc.org for the latest ACCESS-specific interval lists. 
```
/resources/run_files/test.yaml
/resources/run_files/test__collapsing.yaml
/resources/run_tools/luna.yaml
/resources/run_params/test.yaml
/resources/run_params/test__collapsing.yaml
```
For simplicity, its likely that the only values that will actually require any changes are:
```
abra__scratch
tmp_dir
reference_fasta
reference_fasta_fai
bqsr__knownSites_dbSNP
bqsr__knownSites_millis
FP_config_file
A_on_target_positions
B_on_target_positions
noise__good_positions_A
pool_a_bed_file
pool_b_bed_file
gene_list
and the paths to the tools in run_tools
```

### 5. Include the paths to BWA and Bedtools as the first entries in your path:
Abra and pybedtools will use these versions of BWA & bedtools implicitly.  This is not ideal, but remains the only solution for now unless we move to Docker containers
```
PATH="/usr/bin/bwa:$PATH"
PATH="/usr/bin/bedtools:$PATH"
PATH="/usr/bin"
```
This gives us the correct versions of bwa, bedtools and gcc (which are already installed on LUNA)

### 6. Install the python tools
```
(access_pipeline_0.0.26) ~/Innovation-Pipeline$ python setup.py install && python setup.py clean
```

### 7. Install R libraries
These are used by the QC module at the end of the pipeline
```
(access_pipeline_0.0.26) ~/Innovation-Pipeline$ Rscript -e 'install.packages(c("yaml", "dplyr"), repos="http://cran.rstudio.com", lib="~/R")'
```

### 8. Set TMPDIR (optional)
cwltool & toil will use the `TMPDIR` variable for intermediate outputs
```
(access_pipeline_0.0.26) ~/Innovation-Pipeline$ export TMPDIR=/scratch
```

### 9. Set SGE Environment Vars (optional)
If running on Sun Grid Engine workflow scheduler, these will be used to specify the queue, and parallel environment
```
export TOIL_GRIDENGINE_ARGS="-q <queue_name>"
export TOIL_GRIDENGINE_PE="smp"
```

# Running the test pipeline

### 1. Create a run title file from a sample manifest
(example manifests exist in /test/test_data/...)
```
(access_pipeline_0.0.26) ~/my_TEST_run$ create_title_file_from_manifest -i ../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_manifest.xls -o XX_title_file.txt
```

### 2. Create an inputs file from the title file
This step will create a file `inputs.yaml`, and pull in the run parameters (-t for test, -c for collapsing) and paths to run files from step 5.
```
(access_pipeline_0.0.26) ~/my_TEST_run$ create_inputs_from_title_file -i XX_title_file.txt -d ../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer -o inputs.yaml -t -c
```

### 3. Run the test pipeline
To run with the CWL reference implementation (faster for testing purposes):
```
(access_pipeline_0.0.26) ~/my_TEST_run$ cwltool \
  --tmpdir-prefix /where/i/want/tempdirs \
  --tmp-outdir-prefix /where/i/want/outdirs \
  --leave-tmpdir \ # If you want to keep the temp dirs
  --leave-outputs \ # If you want to keep the outputs
  ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
  inputs.yaml
```
To run with Toil batch system runner:
```
(access_pipeline_0.0.26) ~/my_TEST_run$ toil-cwl-runner  ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
```

# Running a real run
I usually start pipeline runs from a consistent directory, with ample storage space. This is where the lsf log files will be written. However, these logs are different from the Toil log files, which will be placed alongside the pipeline outputs as specified by the `output_location` parameter. The log files can be quite large (up to ~50GB if running in debug mode on a large pool). 

Note that there are several valiation requirements when running on your own data:
1. The header names that are found in the sample manifest should matched with the examples in `test/test_data`
2. The sample ID's in the manifest must be matched somewhere in the paths to the fastqs and sample sheets fom the `-d` data folder
4. The pt ids in the manifest must be matched somewhere in the paths to the fastqs and sample sheets fom the `-d` data folder
5. Each sample in the `-d` data folder must have these three files:
```
'_R1_001.fastq.gz'
'_R2_001.fastq.gz'
'SampleSheet.csv'
```
6. The barcode indexes from the manifest/title_file must match what is found in the SampleSheet.csv files

Certain validation requirements can be skipped by using the `-f` parameter in the pipeline kickoff step.

## Example:

### 1. Use the inputs generation scripts

These are the same as when used for running a test with `cwltool` or `toil-cwl-runner`. Note that if there are multiple lanes in the manifest the first script will create multiple title files on a per-lane basis.
```
(access_pipeline_0.0.26) ~/my_REAL_run$ create_title_file_from_manifest -i ~/manifests/ES_manifest.xlsx -o ./ES_title_file.txt
(access_pipeline_0.0.26) ~/my_REAL_run$ create_inputs_from_title_file -i lane-5_ES_title_file.txt -d /home/johnsoni/Data/JAX_0149_AHT3N3BBXX/Project_05500_ES -c -o inputs_lane_5.yaml -f
```

### 2. Use the pipeline runner/submit scripts

Note that we use `pipeline_submit` here to submit both the leader job as well as the worker jobs to the cluster.

Right now the only supported options for the `--batch-system` parameter are `lsf` and `singleMachine`.

```
(access_pipeline_0.0.26) ~/my_REAL_run$ pipeline_submit \
>   --project_name EJ_4-27_MarkDuplicatesTest \
>   --output_location /ifs/work/bergerm1/Innovation/sandbox/ian \
>   --inputs_file ./inputs.yaml \
>   --workflow ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
>   --batch_system lsf
```

Or alternatively, use `pipeline_runner` to make use of the `gridEngine`, `mesos`, `htcondor` or `slurm` options. 

This script can be run in the background with `&`, and will make use of worker nodes for the jobs themselves.

```
(access_pipeline_0.0.26) ~/my_REAL_run$ pipeline_runner \
>   --project_name EJ_4-27_MarkDuplicatesTest \
>   --output_location /ifs/work/bergerm1/Innovation/sandbox/ian \
>   --inputs_file ./inputs.yaml \
>   --workflow ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
>   --batch_system gridEngine
```
This will create the output directory (or restart a failed run in that output directory for `--restart`), and start the workflow using SGE.

### 3. Cleanup the output files
There is a script included to create symlinks to the output bams and delete unnecessary output folders left behind by Toil
```
(access_pipeline_0.0.26) ~$ cleanup_outputs -d <path/to/outputs>
```

### 4. Test the output files
There is a script included to check that the correct samples are paired in the correct folders, and that expected files are present in the final output directory.
```
(access_pipeline_0.0.26) ~$ python -m python_tools.test.test_pipeline_outputs -o <path_to_outputs> -l debug
```

# Issues
Bug reports and questions are helpful, please report any issues, comments, or concerns to the [issues page](https://github.com/mskcc/Innovation-Pipeline/issues)
