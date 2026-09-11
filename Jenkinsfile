pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        MAVEN_OPTS = '-Xmx768m'
        IMAGE_NAME = 'petclinic'
        TEST_HOST = '192.168.56.20'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh '''
                    chmod +x mvnw
                    ./mvnw clean package
                '''
            }

            post {
                always {
                    junit testResults: 'target/surefire-reports/*.xml',
                          allowEmptyResults: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                      -t ${IMAGE_NAME}:${GIT_COMMIT} \
                      .
                '''
            }
        }

        stage('Create Artifact') {
            steps {
                sh '''
                    docker save \
                      ${IMAGE_NAME}:${BUILD_NUMBER} \
                      -o ${IMAGE_NAME}-${BUILD_NUMBER}.tar
                '''
            }
        }

        stage('Archive Artifact') {
            steps {
                archiveArtifacts(
                    artifacts: 'petclinic-*.tar',
                    fingerprint: true
                )
            }
        }

        stage('Deploy to TEST') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'test-deploy-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        mkdir -p ~/.ssh
                        chmod 700 ~/.ssh

                        ssh-keyscan -H ${TEST_HOST} >> ~/.ssh/known_hosts

                        scp -i "$SSH_KEY" \
                          petclinic-${BUILD_NUMBER}.tar \
                          ${SSH_USER}@${TEST_HOST}:/tmp/

                        ssh -i "$SSH_KEY" ${SSH_USER}@${TEST_HOST} "
                          docker load -i /tmp/petclinic-${BUILD_NUMBER}.tar &&
                          docker rm -f petclinic-test-app 2>/dev/null || true
                        "

                        ssh -i "$SSH_KEY" ${SSH_USER}@${TEST_HOST} "
                          docker run -d \
                            --name petclinic-test-app \
                            --restart unless-stopped \
                            --network petclinic-test-net \
                            -p 8080:8080 \
                            -e SPRING_PROFILES_ACTIVE=postgres \
                            -e POSTGRES_URL=jdbc:postgresql://petclinic-test-db:5432/petclinic \
                            -e POSTGRES_USER=petclinic \
                            -e POSTGRES_PASS=petclinic-test \
                            petclinic:${BUILD_NUMBER}
                        "

                        rm -f ~/.ssh/known_hosts
                    '''
                }
            }
        }

        stage('TEST Health Check') {
            steps {
                sh '''
                    echo "Waiting for PetClinic to start..."

                    for i in $(seq 1 30); do
                        if curl -fsS http://${TEST_HOST}:8080/ > /dev/null; then
                            echo "PetClinic TEST environment is healthy"
                            exit 0
                        fi

                        echo "Attempt $i/30 - application not ready yet"
                        sleep 5
                    done

                    echo "Health check failed"
                    exit 1
                '''
            }
        }
    }
}
