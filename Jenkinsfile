pipeline {
    agent any

    environment {
        IMAGE_NAME = 'lost-found-app:latest'
        PYTHON = 'C:\\Users\\Harin\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -q'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t lost-found-app:latest .'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl apply -f deployment.yaml'
                bat 'kubectl apply -f service.yaml'
            }
        }
    }

    post {
        success {
            echo 'Lost and Found application deployed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
