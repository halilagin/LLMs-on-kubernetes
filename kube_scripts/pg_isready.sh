set -a
source llms/$1/llm_agent/.env.kube
pg_isready "$DB_CONNECTION_STRING" 
