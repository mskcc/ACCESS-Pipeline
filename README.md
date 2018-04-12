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
Replace "my-virtual-env" with the name of your virtual environment for this project, e.g. innovation-pipeline
```
~/Innovation-Pipeline$ pip install virtualenvwrapper
~/Innovation-Pipeline$ mkvirtualenv ~/my-virtual-env
~/Innovation-Pipeline$ workon ~/my-virtual-env
(my-virtual-env) ~/Innovation-Pipeline$ add2virtualenv ~/my-virtual-env
```

### 2. Install the python tools
(Make sure your virtualenv is active)
```
(my-virtual-env) ~/Innovation-Pipeline$ python setup.py install
```

### 3. Set the root directory of the project
```
ROOT_DIR = '/Users/johnsoni/Desktop/code/Innovation-Pipeline'
```

### 4. Create a run title file from a sample manifest (Skip to 6 if using existing inputs.yaml)
```
~/Innovation-Pipeline$ create_title_file_from_manifest -i ./manifest.xlsx -o title_file.txt
```

### 5. Create an inputs file from the title file
```
~/Innovation-Pipeline$ create_inputs_from_title_file -i ./test_title_file.txt -d test-data/start -t -l -o
```

### 6. Run the test pipeline
To run with the CWL reference implementation (fastest runtime):
```
~/Innovation-Pipeline$ cwltool --outdir ~/outputs --verbose ../workflows/standard_pipeline.cwl inputs.yaml
```
To run with Toil batch system runner:
```
~/Innovation-Pipeline$ toil-cwl-runner workflows/innovation_pipeline.cwl runs/inputs_pipeline_test.yaml
```
or use:
```
~/Innovation-Pipeline$ test/run-pipeline-test.sh <output_dir>
```
