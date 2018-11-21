#!/usr/bin/env bash

source "$(cd "$(dirname "$0")" ; pwd -P)"/incl.sh

docker stack deploy -c deploy/demos_23_11_18/docker-compose.yml sip

docker stack services sip

echo ""
red_line
docker service ls --format "{{.ID}}: {{.Replicas}} - {{.Name}}"

# Wait for the database to become available.
NAME=sip_config_database
echo -e "${BLUE}* Waiting for service ${NAME} to be ready${NC}"
docker service ls -f name=${NAME}
while true; do
    SERVICE_ID="$(docker service ps -q -f desired-state=running "${NAME}")"
    if [[ ! -z "${SERVICE_ID}" ]]; then
        sleep "1"
        break
    fi
done

# TODO(BMo) Initialise the database?

# Register workflow definitions
skasip_config_db_register_workflows deploy/demos_23_11_18/data/workflow_definitions

