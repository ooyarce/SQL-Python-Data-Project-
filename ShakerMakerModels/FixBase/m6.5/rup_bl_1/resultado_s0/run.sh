#!/bin/bash
parentdir="$(dirname "$(dirname "$(pwd)")")"
dir="$(basename "$(dirname "$(pwd)")")"
subdir="${PWD##*_}"
JOBNAME="${parentdir##*/}_${dir}_${subdir}"
JOBNAME="${JOBNAME: -6}${JOBNAME: -2}"
echo "${JOBNAME}"
