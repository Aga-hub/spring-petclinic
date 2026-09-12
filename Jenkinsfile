pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Te joby mogą pobierać artefakty z CI.
        copyArtifactPermission('deploy-production,rollback-production')
    }

    environment {
        MAVEN_OPTS = '-Xmx768m'

        IMAGE_NAME = 'petclinic'

        TEST_HOST = '192.168.56.20'
        TEST_CONTAINER = 'petclinic-test-app'
        TEST_DB_CONTAINER = 'petclinic-test-db'
        TEST_NETWORK = 'petclinic-test-net'
    }

    stages {

        stage('Checkout') {
            steps {
                // Usuwa stare .tar i inne pozostałości poprzednich buildów.
                deleteDir()

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
                    junit(
                        testResults: 'target/surefire-reports/*.xml',
                        allowEmptyResults: true
                    )
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
                        scp \
                          -o StrictHostKeyChecking=accept-new \
                          -i "$SSH_KEY" \
                          "petclinic-${BUILD_NUMBER}.tar" \
                          "$SSH_USER@$TEST_HOST:/tmp/"

                        ssh \
                          -o StrictHostKeyChecking=accept-new \
                          -i "$SSH_KEY" \
                          "$SSH_USER@$TEST_HOST" \
                          "docker load \
                           -i /tmp/petclinic-${BUILD_NUMBER}.tar &&
                           rm -f /tmp/petclinic-${BUILD_NUMBER}.tar"
                    '''
                }

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'test-deploy-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        ssh \
                          -o StrictHostKeyChecking=accept-new \
                          -i "$SSH_KEY" \
                          "$SSH_USER@$TEST_HOST" \
                          "docker rm -f ${TEST_CONTAINER} \
                           >/dev/null 2>&1 || true;

                           docker run -d \
                           --name ${TEST_CONTAINER} \
                           --restart unless-stopped \
                           --network ${TEST_NETWORK} \
                           -p 8080:8080 \
                           -e SPRING_PROFILES_ACTIVE=postgres \
                           -e POSTGRES_URL=jdbc:postgresql://${TEST_DB_CONTAINER}:5432/petclinic \
                           -e POSTGRES_USER=petclinic \
                           -e POSTGRES_PASS=petclinic-test \
                           ${IMAGE_NAME}:${BUILD_NUMBER}"
                    '''
                }
            }
        }


        stage('TEST Health Check') {
            steps {
                sh '''
                    echo "Waiting for TEST application..."

                    for i in $(seq 1 30); do

                        if curl -fsS \
                          --max-time 5 \
                          http://${TEST_HOST}:8080/ \
                          >/dev/null; then

                            echo "TEST environment is healthy."
                            exit 0
                        fi

                        echo "Attempt $i/30"
                        sleep 5
                    done

                    echo "TEST health check failed."
                    exit 1
                '''
            }
        }


        stage('TEST Smoke Test') {
            steps {
                sh '''
                    curl -fsSL \
                      --max-time 10 \
                      http://${TEST_HOST}:8080/owners/find \
                      >/dev/null

                    curl -fsSL \
                      --max-time 10 \
                      http://${TEST_HOST}:8080/vets.html \
                      >/dev/null
                '''
            }
        }
    }


    post {

        success {
            echo 'CI/TEST pipeline completed successfully.'
        }

        failure {
            echo 'CI/TEST pipeline failed.'
        }

        cleanup {
            deleteDir()
        }
    }
}
