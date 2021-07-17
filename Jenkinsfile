pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id-prod')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key-id-prod')
        STAGE='prod'
        SLS_DEBUG='*'
    }
    stages {
        stage('Clone') {
            steps {
                git(
                    url: 'git@github.com:victorclc/goatfolio-serverless.git',
                    credentialsId: 'github-ssh',
                    branch: 'master'
                )
             }
        }
        stage('Deploy') {
            steps {
                sh 'serverless deploy'
             }
        }
    }
}
