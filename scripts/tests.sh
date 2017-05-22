#!/usr/bin/env bash

PYTHON_COMMAND=${PYTHON_SCRIPT:-python3}

$PYTHON_COMMAND manage.py test --stop --with-coverage --cover-branches  --cover-inclusive --cover-package=monitoreo --settings=conf.settings.testing --exclude=settings --exclude=migrations
