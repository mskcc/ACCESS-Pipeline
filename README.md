### Innovation Pipeline

[![Build Status](https://travis-ci.org/mskcc/Innovation-Pipeline.svg?branch=master)](https://travis-ci.org/mskcc/Innovation-Pipeline)

# Getting Started

Note: These steps are preliminary, and are waiting on consolidation of certain dependencies. Moving to docker containers is the long term solution for this. For now these dependencies must be explicitly installed.  
  - Abra
  - BWA
```
> brew install homebrew/science/bwa/versions/0.7.12
> brew install homebrew/science/bwa
```
  - Samtools
  - Trimgalore
  - Java 7
  - Java 8
  - Python
  - Perl
```
> curl -L https://install.perlbrew.pl | bash
> perlbrew install perl-5.20.2 (might need to try with --notest if install fails)
> source ~/perl5/perlbrew/etc/bashrc
 ```
- HG19 Reference fasta + fai

Note 2: Paths to the tools that are used by the cwl files will need to be manually updated (relative paths aren't an option in `basecommand`)


### 1. Set up a Virtual Environment
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

### 3. Clone the QC module
```
git clone https://github.com/mskcc/Innovation-QC.git
cd Innovation-QC
python setup.py install
```

### 4. Install Dependencies
```
pip install -r requirements.txt 
```

### 5. Update the paths to the tools called in each .cwl CommandLineTool

### 6. Run the test pipeline
```
toil-cwl-runner workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
<or>
test/run-pipeline-test.sh <output_dir>
```
