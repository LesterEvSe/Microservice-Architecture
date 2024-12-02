#!/bin/bash

# TODO Need to test
container_substring=$1
DOCKER_USER="yevheniisekhin"
containers=("calendar" "search" "frontend" "task-service" "user-service")

for container in "${containers[@]}"; do
    if [[ -n $container_substring && $container == *"$container_substring"* ]]; then
        continue
    fi

    docker build -t $DOCKER_USER/$container ./$container
    docker push $DOCKER_USER/$container

    echo "Update deployment $container for Kubernetes"
    kubectl rollout restart deployment/$container
done

echo "The update is successfully completed."
