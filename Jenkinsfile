pipeline {
    agent any
    environment {
        HOME="."
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id-dev')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key-dev')
        SLS_DEBUG='*'
        STAGE='prod'
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
