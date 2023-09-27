#!/usr/bin/env bash

root_dir=llms
llm_package=$1
llm_package_root=$root_dir/$llm_package
llm_package_env_path=$llm_package_root/llm_agent/.env
llm_package_argocd_app_path=$llm_package_root/argocd/020-argocd-application.yaml
llm_package_yamls_path=$llm_package_root/yamls

function deploy(){
kubectl create ns $llm_package
kubectl create configmap -n $llm_package llm-0001 --from-env-file=$llm_package_env_path

}


deploy
