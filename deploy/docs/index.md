# Simple (Django) deploy documentation

## Idea

With this project you'll be able to deploy [this django application](https://gitlab.devartis.com/samples/django-sample).
This repository must allow any (privileged) user to deploy the application.
It must be simple and predictible.
It is tested agains Ubuntu 16.04 at Digital Ocean.

## Specification

See [Idea](docs/idea.md)

## Requirements

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](https://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

### Deploy

For deploying, some extra vars must be passsed:

    export REPO_URL=git@git@example.com/user:repo  # Which repository do you want to deploy?
    export CHECKOUT_BRANCH=master  # Which version (branch or tag)?
    export POSTGRESQL_USER=database_user  # Set psql user name
    export POSTGRESQL_PASSWORD=database_password_xxxxxxx  # Set psql user password
    export HOST=8.8.8.8  # Where do you want to deploy?
    export LOGIN_USER=root  # The user with sudo access.

    bash deploy.sh -r $REPO_URL -p $POSTGRESQL_USER -P $POSTGRESQL_PASSWORD \
        -b $CHECKOUT_BRANCH -h $HOST -l $LOGIN_USER

### Update

For updating, use the update.sh script:

    bash update.sh -r $REPO_URL -b $CHECKOUT_BRANCH -h $HOST -l $LOGIN_USER

## Vagrant & Tests

You can test this project using [Vagrant](https://www.vagrantup.com/):

    export REPO_URL=git@gitlab.devartis.com:samples/django-sample.git
    eval "$(ssh-agent -s) # These two lines allow to pull the project with you ssh keys from gitlab
    ssh-add ~/.ssh/id_rsa
    vagrant up --provision # Setup and run playbook