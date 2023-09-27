#!/bin/bash
export PIPELINE_VERSION=2.0.0
kubectl apply -k kubeflow-pipelines/manifests/kustomize/cluster-scoped-resources
kubectl apply -k kubeflow-pipelines/manifests/kustomize/env/platform-agnostic
    
