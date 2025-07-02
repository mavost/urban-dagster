#!/bin/sh
#set -e
set -x
echo "Entrypoint args: $# - $@"

# Your substitution code...


# Substitute env vars in template
envsubst < $DAGSTER_HOME/dagster.yaml.template > $DAGSTER_HOME/dagster.yaml

if [ $# -eq 0 ]; then
  echo "No args, running dagster-daemon run"
  exec dagster-daemon run
else
  echo "Args present, running exec $@"
  exec "$@"
fi
