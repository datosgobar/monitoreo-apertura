project_name
===============

## Replacing project_name from all files
just change NEW_NAME in the expression below

` find -type f -name "*.*" -not -path "./.git/*" -exec sed -i 's/project_name/NEW_NAME/' {} \; && mv project_name NEW_NAME`

## Requirements:
* Python 2.7
* pip
* [virtualenv](https://virtualenv.readthedocs.org/en/latest/installation.html)/[virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)
    - `sudo pip install virtualenvwrapper`
    - add `source /usr/local/bin/virtualenvwrapper.sh` to your shell config (.bashrs or .zshrs)
    - restart your terminal

## Local Setting's 
* copy settings/local_example.py to settings/local.py.
    - `cp project_name/settings/local_example.py project_name/settings/local.py`
    
## Local setUp
* `mkvirtualenv project_name` or `workon project_name`
* `pip install -r requirements/local.txt`
* `export DJANGO_SETTINGS_MODULE=project_name.settings.local`
* `./manage.py migrate`

## Run server
* `./manage.py runserver`

## Run Lint/Style/CPD:
* pep8: `bash ./git_hooks/pre-push/run_pep8`
* pylint: `bash ./git_hooks/pre-push/run_pylint`
* cpd: `bash ./scripts/cpd.sh`

## Pycharm IDE
* config virtualenv created before as the virtualenv of the project (settings -> python interpreter)
* enable django support: settings -> django 
    - django project root: /home/diego/dev/projects/python/project_name
    - settings: project_name/settings/local.py
    - manage script: manage.py
* mark directory Templates as "Templates folder" (right-click over directory in the "Project view")
