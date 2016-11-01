#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
pylint -f parseable project_name --rcfile=.pylintrc
echo "pylint OK :)"
