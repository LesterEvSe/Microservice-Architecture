#!/bin/bash

substring=$1

# Get all pods
pods=$(kubectl get pods -o=jsonpath='{range .items[*]}{.metadata.name} {"\n"}{end}')

for pod in $pods; do
    if [[ -n $substring && $pod != *$substring* ]]; then
        continue
    fi

    echo "=== Logs for pod: $pod ==="
    kubectl logs $pod
    echo "==========================="
done
