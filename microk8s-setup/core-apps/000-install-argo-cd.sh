#!/bin/bash
helm repo add argo https://argoproj.github.io/argo-helm && helm repo update
helm install --repo https://argoproj.github.io/argo-helm -f argocd-chart-values.yaml --create-namespace --namespace argocd argocd argo-cd --version 5.21.0  --set "configs.cm.application\.resourceTrackingMethod=annotation" --wait
