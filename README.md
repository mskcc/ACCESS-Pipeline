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

# Installation

### 1. Set up a Virtual Environment
Make virtualenv with the name of your virtual environment for this project (e.g. access_pipeline_0.0.16)
```
~$ virtualenv ~/access_pipeline_0.0.16
~$ source ~/access_pipeline_0.0.16/bin/activate
```

### 2. Copy the latest release of the pipeline
(Make sure your virtualenv is active)
```
(access_pipeline_0.0.16) ~$ git clone https://github.com/mskcc/Innovation-Pipeline.git --branch 0.0.3
(access_pipeline_0.0.16) ~$ cd Innovation-Pipeline
```
Alternatively, if you want to pull the latest development version you can use this command (requires to have the tag in the current git repo):
```
(access_pipeline_0.0.16) ~$ git clone https://github.com/mskcc/Innovation-Pipeline.git
(access_pipeline_0.0.16) ~$ git pull --tags
```

### 3. Update the paths to the tool resources and run files
You will need to have your reference files and target lists available. Then provide paths to these files in the following config files. We have two sets of config files available for either running a test run or a real run, but it may be easier to simplify this to just one set. Alternatively, it is also possible to skip this step, and instead create an `inputs.yaml` file manually with paths to you own custom bedfiles. Please contact johnsoni@mskcc.org or patelj1@mskcc.org for the latest ACCESS-specific interval lists. 
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

### 5. Install the python tools
```
(access_pipeline_0.0.16) ~/Innovation-Pipeline$ python setup.py install
```

### 6. Install R libraries
```
(access_pipeline_0.0.16) ~/Innovation-Pipeline$ Rscript -e 'install.packages(c("yaml", "dplyr", "ggrepel"), repos="https://cran.rstudio.com", lib="~/R")'
```

### 7. Copy the test data
It should be possible to use full-sized reference `fasta`, `fai`, `bwt`, `dict`, `vcf`, and `vcf.idx` files, but smaller test versions are located here:
```
(access_pipeline_0.0.16) ~/Innovation-Pipeline$ cp -r /home/johnsoni/test_reference .
```

### 8. Set TMPDIR (optional)
cwltool & toil will use the `TMPDIR` variable for intermediate outputs
```
(access_pipeline_0.0.16) ~/Innovation-Pipeline$ export TMPDIR=/scratch
```

### 9. Set SGE Environment Vars (optional)
If running on Sun Grid Engine workflow scheduler, these will be used to specify the queue, and parallel environment
```
export TOIL_GRIDENGINE_ARGS="-q <queue_name>"
export TOIL_GRIDENGINE_PE="smp"
```

# Running the test pipeline

I usually run the pipelines from a separate directory, with ample storage space. Even though the pipelines outputs directory can be specified for the runs, even the log files can be quite large (up to ~50GB if running in debug mode).

### 1. Create a run title file from a sample manifest
(example manifests exist in /test/test_data/...)
```
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ create_title_file_from_manifest -i Innovation_Pipeline/test/test_data/umi-T_N/manifest.xls -o ./title_file.txt
```

### 2. Create an inputs file from the title file
This step will create a file `inputs.yaml`, and pull in the run parameters (-t for test, -c for collapsing) and paths to run files from step 5.
```
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ create_inputs_from_title_file -i ./test_title_file.txt -d Innovation-Pipeline/test/test-data/umi-T_N -t -c
```

### 3. Run the test pipeline
To run with the CWL reference implementation (faster for testing purposes):
```
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ cwltool \
  --tmpdir-prefix /where/i/want/tempdirs \
  --tmp-outdir-prefix /where/i/want/outdirs \
  --leave-tmpdir \ # If you want to keep the temp dirs
  --leave-outputs \ # If you want to keep the outputs
  ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
  inputs.yaml
```
To run with Toil batch system runner:
```
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ toil-cwl-runner  ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
```

# Running a real run
The same steps for testing can be used for a real run. However this project is still in development, and validation needs to be done on the results of our collapsing steps. In addition, the adapter sequences are hard-coded into the `create_inputs_from_title_file` step, and should be updated as per the barcode-flanking sequences being used. 

Note that there are several requirements when running on your own data:
1. The header names that are found in the sample manifest should matched with the examples in `test/test_data`
2. The sample ID's in the manifest must be matched somewhere in the paths to the fastqs and sample sheets fom the `-d` data folder
4. The pt ids in the manifest must be matched somewhere in the paths to the fastqs and sample sheets fom the `-d` data folder
5. Each sample in the `-d` data folder must have these three files:
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
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ create_title_file_from_manifest -i ./EJ_manifest.xlsx -o ./EJ_title_file.txt
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ create_inputs_from_title_file -i ./EJ_title_file.txt -d ~/data/DY_data -t -c
```
```
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ pipeline_submit \
>   --project_name EJ_4-27_MarkDuplicatesTest \
>   --output_location /ifs/work/bergerm1/Innovation/sandbox/ian \
>   --inputs_file ./inputs.yaml \
>   --workflow ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
>   --batch_system lsf
```
or for other job schedulers:
```
(access_pipeline_0.0.16) ~/PIPELINE_RUNS$ pipeline_runner \
>   --project_name EJ_4-27_MarkDuplicatesTest \
>   --output_location /ifs/work/bergerm1/Innovation/sandbox/ian \
>   --inputs_file ./inputs.yaml \
>   --workflow ~/Innovation-Pipeline/workflows/innovation_pipeline.cwl \
>   --batch_system gridEngine
```
This will create the output directory (or restart a failed run in that output directory for `--restart`), and start the workflow using SGE.

# Issues
Bug reports and questions are helpful, please report any issues, comments, or concerns to the [issues page](https://github.com/mskcc/Innovation-Pipeline/issues)
