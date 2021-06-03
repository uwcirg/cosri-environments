# Cosri Environments

Deployment configuration for COSRI environments.

This README describes how to deploy both COSRI, and the fEMR "free standing" SMART on FHIR host.
If you instead want to deploy COSRI to be used with an existing SMART on FHIR host EHR, see https://github.com/uwcirg/cosri-environments/tree/master/ehr/cosri .


## Setup

### Get Code
Clone this repo to desired location

    git clone https://github.com/uwcirg/cosri-environments


### Configure
Copy the template (`.default`) files in the relevant directory and edit as necessary. Uncommented entries are required and may need to be changed if a default is empty or inappropriate.

    cp default.env .env
