#!/bin/bash

set -e;
set -x;

echo "Agregando clave SSH"
eval "$(ssh-agent -s)"
ssh-add /tmp/build@travis-ci.org

# Nota: Las variables no definidas aqui deben ser seteadas en ./variables.sh

# TODO: Mejorar este script.
echo "Actualizando deployment..."
ssh $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT "\
    cd ~/dev/monitoreo-apertura/deploy/ &&\
    git pull";

ssh $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT "\
    cd ~/dev/monitoreo-apertura/deploy/ &&\
    source ~/dev/venv/bin/activate &&\
    ansible-playbook -i ~/dev/monitoreo-apertura/deploy/inventories/$DEPLOY_ENVIRONMENT/hosts --extra-vars='checkout_branch=$DEPLOY_REVISION' --vault-password-file $DEPLOY_TARGET_VAULT_PASS_FILE site.yml -vv"
