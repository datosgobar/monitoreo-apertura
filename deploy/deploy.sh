#!/usr/bin/env bash

set -e;

INVENTORY=$1
TAG=$2

if [ -z $INVENTORY ]; then
    echo "missing inventory";
    exit 1;
fi

if [ -z $TAG ]; then
    echo "mising tag";
    exit 2;
fi

shift 2;
echo "deploying inventory=$INVENTORY, tag=$TAG";

set -x;
git pull;
ansible-playbook -i inventories/$INVENTORY/hosts --ask-vault-pass --extra-vars=\'checkout_branch=$TAG\' $@ site.yml -vv;