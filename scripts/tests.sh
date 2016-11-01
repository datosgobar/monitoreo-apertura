#!/usr/bin/env bash

PYTHON_COMMAND=${PYTHON_SCRIPT:-python3}

$PYTHON_COMMAND manage.py test --stop --with-coverage --cover-branches  --cover-inclusive --cover-package=project_name --settings=project_name.settings.testing --exclude=settings --exclude=migrations
