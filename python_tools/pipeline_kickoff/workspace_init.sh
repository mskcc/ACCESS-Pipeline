#!/usr/bin/env bash

# This script will set environment variables to run Toil and the ACCESS pipeline tools
# It is LUNA-dependent

# PATH will be set to include the following resources:
# GCC
# Node
# LUNA Bioinformatics tools from /opt/common

export PATH="/opt/common/CentOS_7-dev/bin:/opt/common/CentOS_6-dev/bin/current:/opt/common/CentOS_6-dev/python/python-2.7.10/bin:/common/lsf/9.1/linux2.6-glibc2.3-x86_64/etc:/common/lsf/9.1/linux2.6-glibc2.3-x86_64/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/common/CentOS_6-dev/nodejs/node-v6.10.1/bin/:$PATH"

# Needed for Node.js to find shared libraries
export LD_LIBRARY_PATH="/opt/common/CentOS_6/gcc/gcc-4.9.3/lib64:/common/lsf/9.1/linux2.6-glibc2.3-x86_64/lib:$LD_LIBRARY_PATH"

export TMPDIR=/scratch

export TOIL_LSF_ARGS="-W 3600 -S 1 -app anyOS -R select[type==CentOS7]"