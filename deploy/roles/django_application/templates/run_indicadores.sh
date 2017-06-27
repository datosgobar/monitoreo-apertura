#!/usr/bin/env bash
set -e;


source {{ application_virtualenv_dir }}bin/activate;
export DJANGO_SETTINGS_MODULE=conf.settings.production;
cd {{ application_dir }};
python manage.py indicadores;