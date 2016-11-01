#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}/..

echo "Running pylint"
pylint -f parseable project_name --rcfile=.pylintrc
echo "pylint OK :)"
