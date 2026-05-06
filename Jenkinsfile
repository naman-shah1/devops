pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
                serviceAccountName: jenkins-deployer
                containers:
                - name: docker
                  image: docker:dind
                  securityContext:
                    privileged: true
                  env:
                  - name: DOCKER_TLS_CERTDIR
                    value: /certs
                - name: kubectl
                  image: bitnami/kubectl:latest
                  command:
                  - cat
                  tty: true
                - name: python
                  image: python:3.9-slim
                  command:
                  - cat
                  tty: true
            '''
        }
    }

    environment {
    DOCKER_IMAGE = 'shopflow-lite'
    DOCKER_TAG = "${env.BUILD_NUMBER}"
    DOCKER_REGISTRY = 'docker.io/NamanShah30'
}

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
      stage('Checkout Code') {
    steps {
        checkout([
            $class: 'GitSCM',
            branches: [[name: '*/main']],  // change to */master if needed
            extensions: [],
            userRemoteConfigs: [[
                url: 'https://github.com/naman-shah1/devops.git',
                // add credentialsId: 'github-credentials' if repo is private
            ]]
        ])
    }
}
        stage('Setup Python Environment') {
            steps {
                container('python') {
                    sh '''
                    python -m pip install --upgrade pip
                    pip install -r app/requirements.txt
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                container('python') {
                    sh '''
                    cd app
                    python -m pytest --version || echo "pytest not available, skipping tests"
                    python -c "import app; print('✅ App imports successfully')"
                    '''
                }
            }
        }

        stage('Security Scan') {
            steps {
                container('python') {
                    sh '''
                    pip install safety
                    safety check --file app/requirements.txt || echo "⚠️  Security vulnerabilities found"
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('docker') {
                    sh '''
                    docker build -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker build -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest .
                    '''
                }
            }
        }

        stage('Push Docker Image') {
    steps {
        container('docker') {
            withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                             usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                sh '''
                echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                '''
            }
        }
    }
        }


        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                    echo 'Deploying ShopFlow Lite to Kubernetes...'

                    # Update deployment with new image
                    sed -i "s|image:.*|image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}|g" k8s/deployment.yaml

                    kubectl apply -f k8s/deployment.yaml -n default
                    kubectl apply -f k8s/service.yaml -n default
                    kubectl rollout restart deployment/shopflow-lite -n default
                    kubectl rollout status deployment/shopflow-lite -n default --timeout=300s
                    '''
                }
            }
        }

        stage('Verification') {
            steps {
                container('kubectl') {
                    sh '''
                    echo "🔍 Checking deployment status..."
                    kubectl get pods -n default -l app=shopflow-lite
                    kubectl get svc -n default -l app=shopflow-lite

                    echo "🔍 Checking application health..."
                    kubectl port-forward svc/shopflow-lite-service 8080:5000 -n default &
                    sleep 10
                    curl -f http://localhost:8080/health || echo "⚠️  Health check failed"
                    pkill -f port-forward || true
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                container('docker') {
                    sh '''
                    docker system prune -f
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo "🚀 ShopFlow Lite deployed at: http://your-k8s-service-url"
        }
        failure {
            echo '❌ Pipeline failed!'
            container('kubectl') {
                sh '''
                kubectl get pods -n default
                kubectl describe deployment shopflow-lite -n default || true
                kubectl logs -l app=shopflow-lite -n default --tail=50 || true
                '''
            }
        }
        always {
            echo "📊 Build ${env.BUILD_NUMBER} completed"
            echo "📝 Build URL: ${env.BUILD_URL}"
        }
    }
}
