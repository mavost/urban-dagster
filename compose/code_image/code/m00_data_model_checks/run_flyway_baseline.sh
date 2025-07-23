#!/bin/bash
PG_SERVER=<SINK_SERVER>
PG_PORT=<SINK_PORT>
PG_DB=spotify_sink
PG_USER=spotify_user
PG_PWD=<PASSWORD>
TARGET_SCHEMA=dev
CONTAINER=<CONTAINER_NAME>
CONFIG_FILE="/opt/dagster/app/m00_data_model_checks/flyway_spotify_sink/flyway_$TARGET_SCHEMA.conf"

docker exec \
  -e PG_SERVER=$PG_SERVER \
  -e PG_PORT=$PG_PORT \
  -e PG_DB=$PG_DB \
  -e PG_USER=$PG_USER \
  -e PG_PWD=$PG_PWD \
  -e TARGET_SCHEMA=$TARGET_SCHEMA \
  $CONTAINER \
  flyway -configFiles=$CONFIG_FILE -skipCheckForUpdate -X migrate
# pre-existing databases need to be synced using flyway's baseline command if V1 starts with the initial table/view definitions use migrate instead
# flyway -configFiles=$CONFIG_FILE -skipCheckForUpdate -X baseline
