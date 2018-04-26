### Innovation Pipeline

# Getting Started

Note: These steps are preliminary, and are waiting on consolidation of certain dependencies. Moving to docker containers is the long term solution for this. For now these additional dependencies must be explicitly installed:

| tool | version |
| --- | --- |
| Trimgalore | v0.2.5 |
| Java 7 | jdk1.7.0_75 |
| Java 8 | jdk1.8.0_31 |
| Python | 2.7.10 | 
| Perl | 5.20.2 |
| BWA (must exist in PATH) | 0.7.15-r1140 |
| bedtools (must exist in PATH) | v2.26.0 |
| Marianas | 1.5 |
| Picard | picard-2.8.1.jar | 
| Picard AddOrReplaceReadGroups | AddOrReplaceReadGroups-1.96.jar |
| Picard FixMateInformation | FixMateInformation.jar (1.96) |
| GATK | 3.3.0 |
| Abra | abra-0.92-SNAPSHOT-jar-with-dependencies.jar |

- HG19 Reference fasta + fai
- dbSNP & Millis_100G vcf + .vcf.idx files

# Setup

### 1. Set up a Virtual Environment
Make virtualenv with the name of your virtual environment for this project, e.g. innovation-pipeline
```
~$ virtualenv ~/innovation_pipeline
~$ source ~/innovation_pipeline/bin/activate
```

### 2. Copy the latest release of the pipeline and Install the python tools
(Make sure your virtualenv is active)
(We hope to allow this repo to be cloned from Github once test data storage is confirmed)
```
(innovation_pipeline) ~$ git clone https://github.com/mskcc/Innovation-Pipeline.git --branch 0.0.3
(innovation_pipeline) ~$ cd Innovation-Pipeline-0.0.3
(innovation_pipeline) ~/Innovation-Pipeline-0.0.3$ python setup.py install
```

### 3. Update the paths to the tool resources in `/resources`

### 4. Include the path to BWA as the first entry in your path:
Abra will use this version of BWA implicitly.  This is not ideal, but remains the only solution for now unless we move to Docker containers
```
PATH="/usr/bin/bwa:$PATH"
```

### 5. Set the root directory of the project
(found in `/python_tools/pipeline_kickoff/constants.py`)
```
ROOT_DIR = '/Users/johnsoni/Desktop/code/Innovation-Pipeline'
```

### 6. Create a run title file from a sample manifest 
(example manifest exists in /test/test_data)
```
(innovation_pipeline) ~/Innovation-Pipeline$ create_title_file_from_manifest -i ./manifest.xls -o title_file.txt
```

### 7. Create an inputs file from the title file
This step will create a file `inputs.yaml`, and pull in the run parameters (-t for test params) and paths to run files from step 5.
```
(innovation_pipeline) ~/Innovation-Pipeline$ create_inputs_from_title_file -i ./test_title_file.txt -d test-data/start -t
```

### 8. Run the test pipeline
To run with the CWL reference implementation (faster for testing purposes):
```
(innovation_pipeline) ~/Innovation-Pipeline$ cwltool workflows/standard_pipeline.cwl inputs.yaml
```
To run with Toil batch system runner:
```
(innovation_pipeline) ~/Innovation-Pipeline$ toil-cwl-runner workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
```
or use:
```
(innovation_pipeline) ~/Innovation-Pipeline$ test/run-pipeline-test.sh ~/output_dir
```
Have a look inside `pipeline_runner.sh` to see some useful arguments for Toil & cwltool

# Issues
Bug reports and questions are helpful, please report any issues, comments, or concerns to the [issues page](https://github.com/mskcc/Innovation-Pipeline/issues)
