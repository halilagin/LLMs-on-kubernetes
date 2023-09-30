set -a
source "llms/$1/llm_agent/.env.local"
psql $DB_CONNECTION_STRING -c "${@:2}"
