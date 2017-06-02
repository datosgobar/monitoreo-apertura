#!/usr/bin/env bash
echo "ROOTDIR=$PWD" >> .cronfile
echo "PYTHON=$PWD/../venv/bin/python" >> .cronfile
cat cron_jobs >> .cronfile
crontab .cronfile
rm .cronfile
touch cron_jobs