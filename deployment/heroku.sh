#!/usr/bin/env bash
set -e
if [[ -z "$HEROKU_REMOTE" ]]; then
    echo "Var 'HEROKU_REMOTE' must be set";
    exit 1;
fi

git push $HEROKU_REMOTE HEAD:master
