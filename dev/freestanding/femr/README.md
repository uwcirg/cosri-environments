# Development Environment

Sets up a clone of the production environment locally for development use.


## Setup

Start the containers:

```
cd ./cosri-environments/dev
docker-compose up
```

Finally, navigate to the client: https://dashboard.localtest.me


## Credentials

| Account          | Username | Password |
| ---------------- | -------- | -------- |
| Database Admin   | postgres | postgres |
| Keycloak Admin   | admin    | admin    |
| Application User | test     | test     |
