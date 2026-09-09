pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test pipeline') {
            steps {
                echo 'Jenkins pipeline is working'
            }
        }
    }
}
