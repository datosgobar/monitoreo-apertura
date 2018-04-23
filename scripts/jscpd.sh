#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..


echo "Running jscpd"
npm run jscpd
echo "jscpd OK :)"

