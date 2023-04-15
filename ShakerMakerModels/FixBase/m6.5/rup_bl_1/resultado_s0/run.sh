#!/bin/bash
m=$(basename $(dirname $(dirname $(pwd))) | cut -c 2-)
rup=$(basename $(dirname $(pwd)) | cut -c -5)
result=$(basename $(pwd))
job="${m}_${rup}_${result##*_}"
echo "$job"
