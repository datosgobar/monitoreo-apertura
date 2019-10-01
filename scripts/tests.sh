#!/usr/bin/env bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

python manage.py test --stop --settings=conf.settings.testing --exclude=settings --exclude=migrations
