#!/bin/bash

# Jenkins Pipeline Setup Script for ShopFlow Lite
# This script helps set up the required Kubernetes resources for the Jenkins pipeline

set -e

echo "🚀 Setting up ShopFlow Lite Jenkins Pipeline..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster."
    exit 1
fi

echo "📦 Creating Kubernetes Secret for Supabase credentials..."
kubectl apply -f k8s/secret.yaml

echo "🔐 Creating Service Account for Jenkins..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins-deployer
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: jenkins-deployer-role
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods", "services", "deployments", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: jenkins-deployer-binding
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: jenkins-deployer-role
subjects:
- kind: ServiceAccount
  name: jenkins-deployer
  namespace: default
EOF

echo "✅ Jenkins pipeline setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update DOCKER_REGISTRY in Jenkinsfile with your container registry"
echo "2. Configure Jenkins with Kubernetes cloud and the jenkins-deployer service account"
echo "3. Run the pipeline!"
echo ""
echo "🔗 Application will be available at: http://<node-ip>:30007"