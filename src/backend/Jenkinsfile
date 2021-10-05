pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id-prod')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key-id-prod')
        STAGE='prod'
        SLS_DEBUG='*'
        SES_ARN='arn:aws:ses:sa-east-1:810300526230:identity/noreply@goatfolio.com.br'
        SES_FROM='noreply@goatfolio.com.br'
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
