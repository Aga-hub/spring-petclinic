pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        MAVEN_OPTS = '-Xmx768m'
        IMAGE_NAME = 'petclinic'
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
    }
}
