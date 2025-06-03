# Getting Started

This README assumes the conda environment from `README_IRIS_BAMS.md` has been completed.

Disclaimer: Running the pipeline depends on installation of certain dependencies. Moving to docker containers is the long term solution for this. For now these tools must be previously installed:

External Dependencies
| Tool | Version | Path | Notes
| --- | --- |
| [Vadict](https://github.com/AstraZeneca-NGS/VarDictJava) | 1.8.2 | /home/buehlere/access_tools/VarDictJava/ | installed from source 
| [GBCMS](https://github.com/mskcc/GetBaseCountsMultiSample) | 1.2.5 | /juno/work/access/production/resources/tools/GetBaseCountsMultiSample/versions/GetBaseCountsMultiSample-1.2.5 | Version is still available on Github, but manually copied from Juno. I was having trouble with the install. It still might be possible to build from source.

Additional Vardict install info:
```
./gradlew clean installDist
./gradlew clean javadoc
./gradlew distZip
export PATH=/home/buehlere/access_tools/VarDictJava/VarDict:$PATH
```

### 1. Activate Conda Virtual Environment
```
$ conda activate ACCESS
```

### 2. Update your template variables:

update run_tools parameters in `./ACCESS-PIPELINE/resources/templates/variants.yaml` with one available on IRIS:

```
run_tools:
  bcftools: '/home/buehlere/access_tools/bcftools-1.9/bcftools'
  gbcms: '/home/buehlere/access_tools/GetBaseCountsMultiSample-1.2.5/GetBaseCountsMultiSample'
  java_7: '/admin/software/migration-testing/java/jdk1.7.0_80/bin/java'
  mutect: '/home/buehlere/access_tools/muTect/versions/v1.1.5/muTect-1.1.5.jar'
  vardict: '/home/buehlere/access_tools/VarDictJava/VarDict/vardict'
  vardict_testsomatic: '/home/buehlere/access_tools/VarDictJava/VarDict/testsomatic.R'
  vardict_var2vcf_paired: '/home/buehlere/access_tools/VarDictJava/VarDict/var2vcf_paired.pl'
  perl: '/home/buehlere/miniconda3/envs/ACCESS10/bin/perl'
  vcf2maf: '/home/buehlere/access_tools/vcf2maf/mskcc-vcf2maf-2235eed/vcf2maf.pl'
  vep_path: '/data1/test01/cci/test_data/test_v1_data/vep/v86/'
  vep_data: '/data1/test01/cci/test_data/test_v1_data/vep/cache/'
  tabix: '/home/buehlere/miniconda3/envs/ACCESS10/bin/tabix'
  bgzip: '/home/buehlere/miniconda3/envs/ACCESS10/bin/bgzip'
  sortbed: '/home/buehlere/miniconda3/envs/ACCESS10/bin/sortBed'
  bcftools_1_6: '/home/buehlere/access_tools/bcftools-1.9/bcftools'
```
and re-install:

```
cd ./ACCESS-PIPELINE/
pip install .
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
  --jobStore /scratch/test01/buehlere/store/snv \
  --workDir /scratch/test01/buehlere/work/snv \
  --outdir /data1/test01/cci/output/13102_T/snv \
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
  /home/buehlere/ACCESS-Pipeline/workflows/subworkflows/snps_and_indels.cwl \
  /home/buehlere/access_tests/v1/Project_13102_T_SNV/input.json
```

