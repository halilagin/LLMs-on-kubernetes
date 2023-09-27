set -a
source llm_agent/.env
psql "$DB_CONNECTION_STRING" -c "select 1 as number;"
