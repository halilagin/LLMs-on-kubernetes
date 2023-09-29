kubectl create ns llm-configs
kubectl create configmap -n llm-configs llm-0001 --from-env-file=llm_agent/.env.kube
