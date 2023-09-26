#!/bin/bash
set -a
source llm_agent/.env
set -x
psql $DB_CONNECTION_STRING -f create-embedding-vector-table.sql
