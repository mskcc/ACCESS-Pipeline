### Innovation Pipeline

# Getting Started

Note: These steps are preliminary, and are waiting on consolidation of certain dependencies. Moving to docker containers is the long term solution for this. Some of these dependencies have been aggregated in the `/vendor_tools` folder, but for now these additional dependencies must be explicitly installed:
  - Samtools
  - Trimgalore
  - Java 7
  - Java 8
  - Python
  - BWA
```
If on mac, can be installed with homebrew:
> brew install homebrew/science/bwa/versions/0.7.12
> brew install homebrew/science/bwa
```
  - Perl
```
> curl -L https://install.perlbrew.pl | bash
> perlbrew install perl-5.20.2 (might need to try with --notest if install fails)
> source ~/perl5/perlbrew/etc/bashrc
 ```
- HG19 Reference fasta + fai

Note 2: Paths to the tools that are used by the cwl files will need to be manually updated (relative paths aren't an option in `basecommand`)


# Setup

### 1. Set up a Virtual Environment
(Replace "my-virtual-env" with the name of your virtual environment for this project, e.g. innovation-pipeline)
```
virtualenv ~/my-virtual-env
source ~/my-virtual-env/bin/activate
```

### 2. Set up PATH and PYTHONPATH (put in ~/.profile or ~/.zshrc)
```
export PATH=~/my-virtual-env/bin:$PATH
export PYTHONPATH=~/my-virtual-env/lib/python2.7/site-packages:$PYTHONPATH
```
Note: You may receive errors related to packages being sourced from other locations on the system (e.g. if you have another installation of python or python modules somewhere else, which is likely the case). Make sure that the output from Toil does not reference any of these alternate installations, and only refers to the packages that you installed in `~/my-virtual-env`.

### 4. Install the python tools
(Make sure your virtualenv is active)
```
(my-virtual-env) ~/Innovation-Pipeline$ python setup.py install --prefix ~/my-virtual-env
```

### 5. Clone the QC module (Currently requires manual path manipulation in cwl file)
```
git clone https://github.com/mskcc/Innovation-QC.git
cd Innovation-QC
python setup.py install
```

### 5. Update the paths to the tools called in each .cwl CommandLineTool
This step is currently necessary until the follwing PR is merged:
https://github.com/mskcc/Innovation-Pipeline/pull/2

### 6. Run the test pipeline
To run with the CWL reference implementation (fastest runtime):
```
cwltool workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
```
To run with Toil batch system runner:
```
toil-cwl-runner workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
```
or use:
```
test/run-pipeline-test.sh <output_dir>
```
