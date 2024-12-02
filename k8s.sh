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
else
    echo "Unknown option."
    exit 1
fi

echo ""
kubectl apply -f rabbitmq-and-db.yaml
echo ""

for deployment in rabbitmq user-db task-db; do
    kubectl wait --for=condition=available --timeout=5m deployment/$deployment
done


# Another round for dependent services
echo ""
kubectl apply -f common-services.yaml
echo ""

for deployment in frontend calendar search user-service task-service; do
    kubectl wait --for=condition=available --timeout=5m deployment/$deployment &
done

# Waiting for all background processes to be completed
wait


echo -e "All pods are now ready\n"

echo "Pods"
kubectl get pods

echo -e "\nServices"
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

kubectl port-forward svc/frontend 5000:5000
