# Communere Challenge Project

## About

This is the repository hosting the code for **the entry challenge of Communere**.

## Requirements
- Docker (version 19.03.0 or later)
- Docker compose

## Deploy
- Clone the repo:
`git clone git@github.com:HosseyNJF/todo-challenge.git`
- Copy `.env.example` to `.env`
- Add a new secret key to the local env file
- Run these commands:
```shell
make init
```
- Open the application in the following address:
http://127.0.0.1:5000/swagger-ui
- You can see the OpenAPI/Swagger documentation there.
