export KUBECONFIG=./kubeconfig.kubectl.yaml
kubectl apply -k package/010-preinstall/kubeflow-notebook-controller/apps/jupyter/notebook-controller/upstream/overlays/standalone
