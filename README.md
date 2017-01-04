project_name
===============

[![build status](//gitlab.devartis.com/samples/django-sample/badges/master/build.svg)](http://gitlab.devartis.com/samples/django-sample/commits/master)

## Requirements:
* Python >= 3.4 
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
* Instalar `nodejs` y [jscpd](https://github.com/kucherenko/jscpd)
* pep8: `sh scripts/pep8.sh`
* pylint: `sh scripts/pylint.sh`
* cpd: `sh scripts/jscpd.sh`


## Git hooks
* Bajar binario de [git-hooks](https://github.com/git-hooks/git-hooks/releases) y agregarlo al PATH.
* Instalar hooks: `git hooks install`


## Pycharm IDE
* config virtualenv created before as the virtualenv of the project (settings -> python interpreter)
* enable django support: settings -> django 
    - django project root: /home/diego/dev/projects/python/project_name
    - settings: project_name/settings/local.py
    - manage script: manage.py
* mark directory Templates as "Templates folder" (right-click over directory in the "Project view")

## Project Management

### Rebranding your project

After forking the project you might want to rename both yout project's URL and the URL of the git repo. To do this you need to go to the project settings and on the *Rename repository* section rename both fields.

### Replacing project_name from all files
just change NEW_NAME in the expression below

` find -type f -name "*.*" -not -path "./.git/*" -exec sed -i 's/project_name/NEW_NAME/g' {} \; && mv project_name NEW_NAME`

### Remove fork relation

To be able to use the "New branch" button from an issue, you need to go to project's settings and remove the "Fork relationship" with the sample project. If this is not done, the button will be greyed out and read "New branch unavailable".

See https://gitlab.com/gitlab-org/gitlab-ce/issues/20704

### Copy milestones, issues and labels

We have a template for software development projects (technology agnostic) that specifies some tasks that we need to do in all the projects and labels to categorize issues.

To copy this structure you have to:

1. Install [gitlab-copy](https://github.com/gotsunami/gitlab-copy#download)
1. Get a [Gitlab access token](https://gitlab.devartis.com/profile/personal_access_tokens) and put it on [.gitlab-copy.yml](/.gitlab-copy.yml)
1. Run gitlab-copy: `gitlab-copy -y .gitlab-copy.yml`

### Copy wiki

Attention: Only do this if your wiki is empty. Otherwise you'll need to manually merge the wikis.

1. Clone (if haven't done already) the wiki's git repo from #django-sample/software-development-project-template
 1. `cd /some/random/folder`
 1. `git clone git clone git@gitlab.devartis.com:samples/software-development-project-template.wiki.git`
1. Add to the cloned repo, your project's wiki repo URL as a new remote
 1. `git remote add project_name git@gitlab.devartis.com:group_name/project_name.wiki.git`
1. Push the bse wiki repo to your project's wiki repo
 1. `git push project_name master`

