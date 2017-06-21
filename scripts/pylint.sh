#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
pylint -f parseable monitoreo indicadores_pad --rcfile=.pylintrc
echo "pylint OK :)"
