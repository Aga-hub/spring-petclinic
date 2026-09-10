pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        MAVEN_OPTS = '-Xmx768m'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Compile') {
            steps {
                sh '''
                    chmod +x mvnw
                    ./mvnw clean compile
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh './mvnw test'
            }

            post {
                always {
                    junit testResults: 'target/surefire-reports/*.xml',
                          allowEmptyResults: true
                }
            }
        }
    }
}
