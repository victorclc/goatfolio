# goatfolio-serverless

It's the back-end of the goatfolio_app.

## What is Goatfolio

It's (or it's becoming) a investment portfolio tracking app for brazilian investors.

## Project organization

### services/

This project it's a mono-repo for multiple services. All services have your own directory inside services/ with its specific serverless.yml containing all CloudFormation templates necessary for the service

### libs/

Contain all code that may be shared between services.

### /

Has a serverless.yml file with all aws resources that needs to be shared between two or more services.
