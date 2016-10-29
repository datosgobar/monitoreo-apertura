#!/usr/bin/env bash

#!/usr/bin/env bash
set -e
if [[ -z "$AZURE_DEPLOY_USER" || -z "$AZURE_DEPLOY_PASSWORD" || -z "$AZURE_DEPLOY_TESTING_HOST" || -z "$AZURE_DEPLOY_PATH" ]]; then
    echo "Variables 'AZURE_DEPLOY_USER', 'AZURE_DEPLOY_PASSWORD', 'AZURE_DEPLOY_TESTING_HOST' and 'AZURE_DEPLOY_PATH' must be set";
    exit 1;
fi


git push https://$AZURE_DEPLOY_USER:$AZURE_DEPLOY_PASSWORD@$AZURE_DEPLOY_TESTING_HOST/$AZURE_DEPLOY_PATH HEAD:master
