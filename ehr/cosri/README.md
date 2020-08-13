# Cosri Environments

Deployment config for Cosri environments


## Setup

### Get Code
Clone this repo to desired location

git clone https://github.com/uwcirg/cosri-environments


### Configure
Copy the template (`.default`) files in the relevant directory and edit as necessary. Uncommented entries are required and may need to be changed if a default is empty or inappropriate.

```
cp default.env .env
```

### Start Services
If running locally, start the traefik ingress proxy first


Start all services
docker-compose up --detach


### Development
To configure services for development, add the corresponding `docker-compose.dev.yaml` override to `COMPOSE_FILE`
