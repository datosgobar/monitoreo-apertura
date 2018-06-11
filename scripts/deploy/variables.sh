#!/usr/bin/env bash

ENVIRONMENT="$1"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# NOTA: para agregar un nuevo ambiente, se necesitan todas estas variables,
# pero usando otros prefijos (en testing es TESTING_* )

export OVPN_CONFIG="client"
export OVPN_PATH="/etc/openvpn/$OVPN_CONFIG.conf"

# Las siguientes variables definen cuales variables buscar para desencriptar
# algunos valores de travis. Ver ./prepare.sh para mas info

DEFAULT_MTU_VALUE=578

if [ "$ENVIRONMENT" == "testing" ]; then
    echo "Ambiente $ENVIRONMENT"

    export USE_VPN="$TESTING_USE_VPN"

    export DEPLOY_TARGET_VAULT_PASS_FILE="$TESTING_DEPLOY_VAULT_PASS_FILE"
    export DEPLOY_TARGET_SSH_PORT="$TESTING_DEPLOY_TARGET_SSH_PORT"
    export DEPLOY_TARGET_USERNAME="$TESTING_DEPLOY_TARGET_USERNAME"
    export DEPLOY_TARGET_IP="$TESTING_DEPLOY_TARGET_IP"
    export DEPLOY_ENVIRONMENT="$ENVIRONMENT"
    export MTU_VALUE="${STIEMPO_DEV_MTU_VALUE:-$DEFAULT_MTU_VALUE}"
    export DEPLOY_REVISION="master"
else
    echo "Ambiente '$ENVIRONMENT' desconocido";
    exit 1;
fi
