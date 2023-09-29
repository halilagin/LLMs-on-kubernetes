#!/bin/bash
set -a
source llm_agent/.env.local
psql $DB_CONNECTION_STRING -c "CREATE EXTENSION vector;"
