#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}/..


echo "Running jscpd"
jscpd --verbose --o /dev/null --limit 1
echo "jscpd OK :)"

