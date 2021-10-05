# goatfolio-serverless

It's the back-end of the goatfolio_app.


## CI/CD
### Master
[![cei-crawler](https://github.com/victorclc/goatfolio-serverless/actions/workflows/cei-crawler.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/cei-crawler.yml)
[![corporate-events](https://github.com/victorclc/goatfolio-serverless/actions/workflows/corporate-events.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/corporate-events.yml)
[![event-notifier](https://github.com/victorclc/goatfolio-serverless/actions/workflows/event-notifier.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/event-notifier.yml)
[![goatfolio-serverless](https://github.com/victorclc/goatfolio-serverless/actions/workflows/goatfolio-serverless.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/goatfolio-serverless.yml)
[![market-history](https://github.com/victorclc/goatfolio-serverless/actions/workflows/market-history.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/market-history.yml)
[![performance-api](https://github.com/victorclc/goatfolio-serverless/actions/workflows/performance-api.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/performance-api.yml)
[![portfolio-api](https://github.com/victorclc/goatfolio-serverless/actions/workflows/portfolio-api.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/portfolio-api.yml)
[![push-notifications](https://github.com/victorclc/goatfolio-serverless/actions/workflows/push-notifications.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/push-notifications.yml)
[![vandelay-api](https://github.com/victorclc/goatfolio-serverless/actions/workflows/vandelay-api.yml/badge.svg)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/vandelay-api.yml)

### Develop
[![cei-crawler](https://github.com/victorclc/goatfolio-serverless/actions/workflows/cei-crawler.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/cei-crawler.yml)
[![corporate-events](https://github.com/victorclc/goatfolio-serverless/actions/workflows/corporate-events.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/corporate-events.yml)
[![event-notifier](https://github.com/victorclc/goatfolio-serverless/actions/workflows/event-notifier.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/event-notifier.yml)
[![goatfolio-serverless](https://github.com/victorclc/goatfolio-serverless/actions/workflows/goatfolio-serverless.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/goatfolio-serverless.yml)
[![market-history](https://github.com/victorclc/goatfolio-serverless/actions/workflows/market-history.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/market-history.yml)
[![performance-api](https://github.com/victorclc/goatfolio-serverless/actions/workflows/performance-api.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/performance-api.yml)
[![portfolio-api](https://github.com/victorclc/goatfolio-serverless/actions/workflows/portfolio-api.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/portfolio-api.yml)
[![push-notifications](https://github.com/victorclc/goatfolio-serverless/actions/workflows/push-notifications.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/push-notifications.yml)
[![vandelay-api](https://github.com/victorclc/goatfolio-serverless/actions/workflows/vandelay-api.yml/badge.svg?branch=develop)](https://github.com/victorclc/goatfolio-serverless/actions/workflows/vandelay-api.yml)

## What is Goatfolio

It's (or it's becoming) a investment portfolio tracking app for brazilian investors.

## Project organization

### services/

This project it's a mono-repo for multiple services. All services have your own directory inside services/ with its specific serverless.yml containing all CloudFormation templates necessary for the service

### libs/

Contain all code that may be shared between services.

### /

Has a serverless.yml file with all aws resources that needs to be shared between two or more services.
