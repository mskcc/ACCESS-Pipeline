#!/bin/bash
# ----------------------------------------------------------------------------------------------------
# Title:       setup.sh
# Description: Setup conda environment for ACCESS pipeline and install all the python and R libraries.
# Dependency:  conda>=4.5.4
# Usage:       ./setup.sh <optional environment name>
# -----------------------------------------------------------------------------------------------------

#############
# Functions #
#############

HOSTNAME=$(hostname -s)

function printe () {
        printf "$HOSTNAME::$(date +'%T')::ERROR $@\n\n"
}

function printi () {
        printf "$HOSTNAME::$(date +'%T')::INFO $@\n\n"
}

function cleanup() {
        EXITCODE=$?
        if [[ $EXITCODE != 0 ]] & [[ -e ${ACCESS_ENV} ]]; then
		source deactivate
                printe "Installation unsuccessful. Removing conda environment: ${ACCESS_ENV}"
                conda env remove -n ${ACCESS_ENV}
	elif [[ $EXITCODE == 0  ]]; then
		source deactivate
	fi
        exit $EXITCODE
}
trap cleanup EXIT


###########################
# Setup Conda Environment #
###########################

# Check for environment name
ACCESS_ENV=$1
[[ ! -z $ACCESS_ENV ]] || { printi "No preferred environment name given. Conda environment name will be set to 'ACCESS'";  ACCESS_ENV="ACCESS"; }

# set library paths
[[ ! -z "${LIBRARY_PATH}" ]] || { printi "LIBRARY_PATH not set. Will be default to /usr/lib64"; export LIBRARY_PATH="/usr/lib64"; }

[[ ! -z "${LD_LIBRARY_PATH}" ]] || { printi "LD_LIBRARY_PATH not set. Will be defaulted to /usr/lib64"; export LD_LIRBARY_PATH="/usr/lib64"; }

# Check for conda installation
type -p conda > /dev/null || { printe "Conda installation is required! Visit https://www.anaconda.com/distribution/"; exit 1; }

# Set pythonpath and rlibs variables to empty string.
export PYTHONPATH=""
export R_LIBS=""

# TODO:
# Upgrade/Downgrade conda version?

[[ -e "${PWD}/environment.yaml" ]] || { printe "${PWD}/environment.yaml not found."; exit 1; }

# get conda path
CONDA=$(type -p conda | sed "s/conda is //")
[[ -e $CONDA ]] || { printe "Cannot find conda binary. Make sure conda is added to your PATH variable."; exit 1; }

printi "Creating conda environment: $ACCESS_ENV"
conda env create --name $ACCESS_ENV --file $PWD/environment.yaml

EXITCODE=$?
[[ $EXITCODE == 0 ]] || exit $EXITCODE;

# TODO:
# Use conda pre-built R libraries. Since some of the libraries are in dev, lets install it using R for now.
# Activate environment
printi "Activating ${ACCESS_ENV}"
source activate ${ACCESS_ENV}
[[ $EXITCODE == 0 ]] || { printe "Cannot activate ${ACCESS_ENV}."; exit $EXITCODE; }

RSCRIPT=$(echo $CONDA | sed "s/bin\/conda/envs\/${ACCESS_ENV}\/bin\/Rscript/")

[[ -e "$RSCRIPT" ]] || { printe "Cannot locate Rscript in the environment $ACCESS_ENV. Was your environment setup properly?"; exit 1; }

printi "Installing R packages from CRAN..."
$RSCRIPT -e 'install.packages(c("devtools","grid","yaml","scales","gridBase","gridExtra","lattice","ggplot2","getopt","reshape2","dplyr","tidyr","data.table","MASS","gplots","RColorBrewer","DNAcopy","Ckmeans.1d.dp","rjson","curl"), repos="https://cran.cnr.berkeley.edu/")'

EXITCODE=$?
[[ $EXITCODE == 0 ]] || { printe "Error during R package installation from CRAN."; exit $EXITCODE; }

printi "Installing R packages from source..."
$RSCRIPT -e 'install.packages(install.packages("http://bioconductor.org/packages/release/bioc/src/contrib/DNAcopy_1.58.0.tar.gz", repos=NULL, type="source")'

EXITCODE=$?
[[ $EXITCODE == 0 ]] || { printe "Error during R package installation from source."; exit $EXITCODE; }

print "Installing R packages from github..."
$RSCRIPT -e 'library(devtools); install_github("rptashkin/textplot", force=TRUE);'

EXITCODE=$?
[[ $EXITCODE == 0 ]] || { printe "Error during R package installation from github."; exit $EXITCODE; }

printi "ACCESS environment setup complete! \^.^/"

