#!/usr/bin/env bash
set -e;
if [ -z "$SSH_PRIVATE_KEY" ]; then
    echo "SSH_PRIVATE_KEY must be defined"
fi
eval $(ssh-agent -s)
ssh-add <(echo "$SSH_PRIVATE_KEY")
if [ -z "$UPDATE_TASK" ]; then
    bash deploy.sh -r $REPO_URL -b $BRANCH -p $POSTGRES_USER $POSTGRES_PASSWIRD -h $HOST -l $USER -u
else    
    bash deploy.sh -r $REPO_URL -b $BRANCH -p $POSTGRES_USER $POSTGRES_PASSWIRD -h $HOST -l $USER
fi
