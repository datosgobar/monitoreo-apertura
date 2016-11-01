#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}/..


echo "Running pep8"
pep8 project_name --max-line-length=140 --ignore=E731 --exclude=**/migrations/,__init__.py

echo "pep8 OK :)"
