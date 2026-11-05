
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'ghcr.io/mukesh-sankaran/taskflow-devops'
        IMAGE_TAG = "${GIT_COMMIT}"
        PATH = "/opt/homebrew/bin:/usr/local/bin:${env.PATH}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Lint - Ruff') {
            steps {
                sh '''
                    python3 -m venv .venv-ci
                    .venv-ci/bin/pip install -r requirements-dev.txt
                    .venv-ci/bin/ruff check .
                '''
            }
        }

        stage('Test - pytest') {
            steps {
                sh '''
                    .venv-ci/bin/pytest -v
                '''
            }
        }

        stage('Security Scan - Trivy') {
            steps {
                sh '''
                    trivy fs \
                      --scanners vuln,misconfig,secret \
                      --severity HIGH,CRITICAL \
                      --exit-code 1 \
                      --ignore-unfixed \
                      .
                '''
            }
        }

        stage('Build - Docker') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      .
                '''
            }
        }

        stage('Push - GHCR') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-creds',
                        usernameVariable: 'GHCR_USER',
                        passwordVariable: 'GHCR_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$GHCR_TOKEN" | docker login ghcr.io \
                          -u "$GHCR_USER" --password-stdin

                        docker push ${IMAGE_NAME}:${IMAGE_TAG}

                        docker logout ghcr.io
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'TaskFlow CI pipeline completed successfully!'
            echo "Published image: ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo 'TaskFlow CI pipeline failed. Check the stage logs.'
        }
    }
}
