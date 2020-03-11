#!/bin/bash
# ----------------------------------------------------------------------------------------------------
# Title:       setup.sh
# Description: Setup conda environment for ACCESS pipeline and install all the python and R libraries.
# Dependency:  conda>=4.6.14; environment.yaml (in the same directory as this script)
# Usage:       ./setup.sh <optional_environment_name>
# ----------------------------------------------------------------------------------------------------

#############
# Functions #
#############

HOSTNAME=$(hostname -s)

function printe () {
	# print error message
        printf "\n$HOSTNAME::$(date +'%T')::ERROR $@\n"
}

function printi () {
	# print info
        printf "\n$HOSTNAME::$(date +'%T')::INFO $@\n"
}

function cleanup() {
	# Housekeeping function that will run at the end regardless of 
	# exit status. Upon successful setup, deactivate environment.
	# If setup is unsuccessful at any stage, remove the environment.
        EXITCODE=$?
        if [[ $EXITCODE != 0 ]] && [[ -e ${ACCESS_ENV_PATH} ]]; then
		source deactivate
                printe "Installation unsuccessful. Removing conda environment: ${ACCESS_ENV}"
                conda env remove -n ${ACCESS_ENV}
	fi
        exit $EXITCODE
}
trap cleanup EXIT


###########################
# Setup Conda Environment #
###########################

# Check for environment name
ACCESS_ENV=$1
[[ ! -z $ACCESS_ENV ]] || {
        printi "No preferred environment name given. Conda environment name will be set to 'ACCESS'";
        ACCESS_ENV="ACCESS";
        }

# set library paths
[[ ! -z "${LIBRARY_PATH}" ]] || {
        printi "LIBRARY_PATH not set. Will be default to /usr/lib64";
        export LIBRARY_PATH="/usr/lib64";
        }

[[ ! -z "${LD_LIBRARY_PATH}" ]] || {
        printi "LD_LIBRARY_PATH not set. Will be defaulted to /usr/lib64";
        export LD_LIRBARY_PATH="/usr/lib64";
        }

# Check for conda installation
type -p conda > /dev/null || {
        printe "Conda installation is required! Visit https://www.anaconda.com/distribution/";
        exit 1;
        }

# Set pythonpath
export PYTHONPATH="" # to avoid conflicts with system python libraries

# TODO:
# Upgrade/Downgrade conda version?

[[ -e "${PWD}/environment.yaml" ]] || {
        printe "${PWD}/environment.yaml not found."; 
        exit 1;
        }

# get conda path
CONDA=$(type -p conda | sed "s/conda is //")
[[ -e $CONDA ]] || {
        printe "Cannot find conda binary. Make sure conda is added to your PATH variable.";
        exit 1;
        }

# ensure that no other env with the same name exist
ACCESS_ENV_PATH=$(echo $CONDA | sed "s/bin\/conda/envs\/${ACCESS_ENV}/")
[[ ! -e ${ACCESS_ENV_PATH} ]] || {
        printi "${ACCESS_ENV_PATH} already exist.";
        exit 0;
        }

printi "Creating conda environment: $ACCESS_ENV"
conda env create --name $ACCESS_ENV --file $PWD/environment.yaml

EXITCODE=$?
[[ $EXITCODE == 0 ]] || exit $EXITCODE;

printi "ACCESS environment setup complete! \^.^/"
source deactivate
