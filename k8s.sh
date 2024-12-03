#!/bin/bash

if [[ "$1" == "start" ]]; then
    minikube start
elif [[ "$1" == "restart" ]]; then
    kubectl delete -f rabbitmq-and-db.yaml
    kubectl delete -f common-services.yaml
elif [[ "$1" == "prune" ]]; then
    minikube stop
    minikube delete
    exit 0
fi

apply_and_wait() {
    local file=$1
    local deployments=("${@:2}")

    echo ""
    kubectl apply -f "$file"
    echo ""

    for deployment in "${deployments[@]}"; do
        kubectl wait --for=condition=available --timeout=5m deployment/"$deployment" &
    done
    wait
}

# First, the main services should start, and then those that depend on them
apply_and_wait rabbitmq-and-db.yaml rabbitmq user-db task-db
apply_and_wait common-services.yaml frontend calendar search user-service task-service


echo -e "All pods are ready now.\n"

echo "========= Pods ==========="
kubectl get pods

echo -e "\n======= Services ========="
kubectl get services


# get names list
if [[ "$2" == "info" ]]; then
    echo -e "\nPods describe"
    pod_names=$(kubectl get pods --no-headers -o custom-columns=":metadata.name")

    for pod_name in $pod_names; do
        echo "Describing pod: $pod_name"
        kubectl describe pod "$pod_name"
        echo -e "\n\n"
    done
fi

# To be able to connect from a localhost, i.e. an external device
kubectl port-forward svc/frontend 5000:5000
