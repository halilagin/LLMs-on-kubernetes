#!/bin/bash
set -a
source llm_agent/.env.kube
psql $DB_CONNECTION_STRING -c "CREATE EXTENSION vector;"
