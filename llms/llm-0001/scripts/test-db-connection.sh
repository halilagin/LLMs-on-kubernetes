set -a
source llms/$1/llm_agent/.env
psql "$DB_CONNECTION_STRING" -c "select 1 as number;"
