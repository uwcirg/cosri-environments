# Cosri Environments

Deployment config for Cosri environments

This README describes how to deploy COSRI to be used with an existing SMART on FHIR host EHR. If you want to instead deploy both COSRI, and the fEMR "free standing" SMART on FHIR host, see https://github.com/uwcirg/cosri-environments/blob/master/README.md .

## Setup

### Get Code
Clone this repo to desired location

git clone https://github.com/uwcirg/cosri-environments


### Configure
Copy the template (`.default`) files in the relevant directory and edit as necessary. Uncommented entries are required and may need to be changed if a default is empty or inappropriate.

```
cp default.env .env
```
Copy the HTTP client certificates necessary (`pdmp.crt` and `pdmp.key`) for PDMP access into the [certificates directory](./config/pdmp/certs)

### Start Services
If running locally, start the traefik ingress proxy first (See [extras directory](../../extras))


Start all services
docker-compose up --detach


### Launch
To launch from the [SMART Health IT Launcher](https://launch.smarthealthit.org), set the Launch URL to:
https://backend.$BASE_DOMAIN/auth/launch

### Development
To configure services for development, add the corresponding `docker-compose.dev.yaml` override to `COMPOSE_FILE`
