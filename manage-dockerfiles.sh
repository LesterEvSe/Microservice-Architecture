#!/bin/bash

container_substring=$1
DOCKER_USER="yevheniisekhin"
containers=("calendar" "search" "frontend" "task-service" "user-service")

minikube status &> /dev/null
if [ $? -ne 0 ]; then
    minikube start
fi

echo $container_substring
for container in "${containers[@]}"; do
    if [[ -n $container_substring && $container != *"$container_substring"* ]]; then
        continue
    fi
    
    # Deprecated builder. I do not for now, what to do with it...
    docker build -t $DOCKER_USER/$container ./$container
    docker push $DOCKER_USER/$container
    echo ""
done

echo "The update is successfully completed."
