set -a
source llms/$1/llm_agent/.env.local
pg_isready "$DB_CONNECTION_STRING" 
